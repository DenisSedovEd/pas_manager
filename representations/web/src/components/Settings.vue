<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { resourceApi } from '../api/resource.js'
import {
  customIconApi,
  customIconFileUrl,
  isCustomIcon,
} from '../api/customIcon.js'
import CategoryIcon from './CategoryIcon.vue'
import EmojiPicker from 'vue3-emoji-picker'
import 'vue3-emoji-picker/css'

const props = defineProps({
  resources: { type: Array, default: () => [] },
})
const emit = defineEmits(['back', 'resources-updated'])

const localResources = ref([])
const editing = ref(null)
const isLoading = ref(false)
const showPicker = ref(false)
const pickerTab = ref('emoji')
const customIcons = ref([])
const isUploading = ref(false)
const fileInput = ref(null)

const formData = ref({
  id: null,
  resource_name: '',
  description: '',
  icon: null,
})

const selectedCustomId = computed(() => {
  if (!isCustomIcon(formData.value.icon)) return null
  return formData.value.icon.slice('custom:'.length)
})

const syncLocal = () => {
  localResources.value = [...props.resources].sort((a, b) =>
    (a.resource_name || '').localeCompare(b.resource_name || '', 'ru')
  )
}

const loadCustomIcons = async () => {
  customIcons.value = await customIconApi.getList()
}

const openEdit = (resource) => {
  editing.value = resource
  formData.value = {
    id: resource.id,
    resource_name: resource.resource_name || '',
    description: resource.description || '',
    icon: resource.icon || null,
  }
  showPicker.value = false
  pickerTab.value = isCustomIcon(resource.icon) ? 'custom' : 'emoji'
}

const cancelEdit = () => {
  editing.value = null
  showPicker.value = false
}

const onSelectEmoji = (emoji) => {
  formData.value.icon = emoji.i
  showPicker.value = false
}

const onSelectCustom = (icon) => {
  formData.value.icon = icon.key
  showPicker.value = false
}

const clearIcon = () => {
  formData.value.icon = null
  showPicker.value = false
}

const openFilePicker = () => {
  fileInput.value?.click()
}

const onFileSelected = async (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  isUploading.value = true
  try {
    const created = await customIconApi.upload(file)
    customIcons.value = [created, ...customIcons.value]
    formData.value.icon = created.key
    showPicker.value = false
  } catch (err) {
    alert(err.message || 'Ошибка загрузки иконки')
  } finally {
    isUploading.value = false
  }
}

const deleteCustom = async (icon, event) => {
  event.stopPropagation()
  if (!confirm('Удалить эту иконку?')) return
  try {
    await customIconApi.delete(icon.id)
    customIcons.value = customIcons.value.filter((item) => item.id !== icon.id)
    if (formData.value.icon === icon.key) {
      formData.value.icon = null
    }
    localResources.value = localResources.value.map((r) =>
      r.icon === icon.key ? { ...r, icon: null } : r
    )
    emit('resources-updated', localResources.value)
  } catch {
    alert('Ошибка удаления иконки')
  }
}

const isDefaultResource = computed(
  () => editing.value?.resource_name === 'Без площадки'
)

const handleSave = async () => {
  if (!formData.value.resource_name.trim()) {
    alert('Введи название площадки')
    return
  }
  isLoading.value = true
  try {
    const updated = await resourceApi.update(formData.value.id, {
      resource_name: formData.value.resource_name.trim(),
      description: formData.value.description || null,
      icon: formData.value.icon || null,
    })
    localResources.value = localResources.value
      .map((r) => (r.id === updated.id ? updated : r))
      .sort((a, b) =>
        (a.resource_name || '').localeCompare(b.resource_name || '', 'ru')
      )
    emit('resources-updated', localResources.value)
    editing.value = null
  } catch (err) {
    alert(err.message || 'Ошибка при сохранении')
  } finally {
    isLoading.value = false
  }
}

const handleDelete = async () => {
  if (isDefaultResource.value) {
    alert('Нельзя удалить системную площадку «Без площадки»')
    return
  }
  if (!confirm(
    `Удалить площадку «${formData.value.resource_name}»?\nАккаунты будут перенесены на «Без площадки».`
  )) return
  isLoading.value = true
  try {
    await resourceApi.delete(formData.value.id)
    localResources.value = localResources.value.filter((r) => r.id !== formData.value.id)
    emit('resources-updated', localResources.value)
    editing.value = null
  } catch (err) {
    alert(err.message || 'Ошибка при удалении')
  } finally {
    isLoading.value = false
  }
}

watch(() => props.resources, syncLocal, { deep: true })

onMounted(async () => {
  syncLocal()
  try {
    await loadCustomIcons()
  } catch {
    // галерея подтянется при открытии вкладки
  }
})
</script>

<template>
  <div class="settings-page">
    <div class="screen-header">
      <button class="sub-back-btn" @click="editing ? cancelEdit() : $emit('back')">⬅️</button>
      <h2>{{ editing ? 'Площадка' : 'Настройки' }}</h2>
    </div>

    <template v-if="!editing">
      <p class="section-hint">Площадки — переименование, иконка и удаление. При удалении аккаунты переносятся на «Без площадки».</p>
      <div v-if="!localResources.length" class="empty">Нет площадок</div>
      <div v-else class="list">
        <div
          v-for="resource in localResources"
          :key="resource.id"
          class="list-item"
          @click="openEdit(resource)"
        >
          <div class="item-icon-box">
            <CategoryIcon :icon="resource.icon" fallback="🌐" size="lg" />
          </div>
          <div class="item-info">
            <span class="item-name">{{ resource.resource_name }}</span>
            <span v-if="resource.description" class="item-sub">{{ resource.description }}</span>
            <span v-else-if="!resource.icon" class="item-sub">Иконка категории</span>
          </div>
          <span class="chevron">›</span>
        </div>
      </div>
    </template>

    <div v-else class="form">
      <div class="icon-section">
        <div class="icon-wrapper" @click="showPicker = !showPicker">
          <div class="icon-preview">
            <CategoryIcon :icon="formData.icon" fallback="🌐" size="xl" />
          </div>
          <div class="edit-badge">{{ showPicker ? '✕' : '⚙️' }}</div>
        </div>
        <p class="hint">
          {{ formData.icon ? 'Нажми, чтобы изменить' : 'Нет своей иконки — у аккаунтов будет иконка категории' }}
        </p>
        <button v-if="formData.icon" type="button" class="clear-icon-btn" @click="clearIcon">
          Сбросить (иконка категории)
        </button>
        <div v-if="showPicker" class="picker-container">
          <div class="picker-tabs">
            <button
              type="button"
              class="picker-tab"
              :class="{ active: pickerTab === 'emoji' }"
              @click="pickerTab = 'emoji'"
            >Эмодзи</button>
            <button
              type="button"
              class="picker-tab"
              :class="{ active: pickerTab === 'custom' }"
              @click="pickerTab = 'custom'"
            >Свои</button>
          </div>

          <EmojiPicker
            v-if="pickerTab === 'emoji'"
            :native="true"
            @select="onSelectEmoji"
          />

          <div v-else class="custom-panel">
            <input
              ref="fileInput"
              type="file"
              accept="image/png,image/jpeg,image/webp,image/svg+xml"
              class="file-input"
              @change="onFileSelected"
            />
            <button
              type="button"
              class="upload-btn"
              :disabled="isUploading"
              @click="openFilePicker"
            >
              {{ isUploading ? 'Загрузка...' : '+ Загрузить иконку' }}
            </button>
            <p class="upload-hint">PNG, JPEG, WebP или SVG, до 512 KB</p>

            <div v-if="!customIcons.length" class="custom-empty">Пока нет своих иконок</div>
            <div v-else class="custom-grid">
              <button
                v-for="icon in customIcons"
                :key="icon.id"
                type="button"
                class="custom-item"
                :class="{ selected: selectedCustomId === icon.id }"
                @click="onSelectCustom(icon)"
              >
                <img :src="customIconFileUrl(icon.key)" alt="" class="custom-thumb" />
                <span
                  class="custom-delete"
                  title="Удалить"
                  @click="deleteCustom(icon, $event)"
                >✕</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label>Название *</label>
        <input v-model="formData.resource_name" type="text" placeholder="Например: GitHub" />
      </div>

      <div class="form-group">
        <label>Описание (необязательно)</label>
        <input v-model="formData.description" type="text" placeholder="Краткое описание" />
      </div>

      <div class="form-actions">
        <button class="btn-primary" :disabled="isLoading" @click="handleSave">
          {{ isLoading ? 'Сохранение...' : 'Сохранить' }}
        </button>
        <button class="btn-secondary" @click="cancelEdit">Отмена</button>
      </div>
      <button
        v-if="!isDefaultResource"
        type="button"
        class="btn-danger"
        :disabled="isLoading"
        @click="handleDelete"
      >
        Удалить площадку
      </button>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  width: min(100%, 480px);
  margin: 0 auto;
  padding: 0 0 2rem;
}

.screen-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.screen-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.sub-back-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
}

.section-hint {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: var(--color-hint);
  line-height: 1.4;
}

.empty {
  text-align: center;
  color: var(--color-hint);
  padding: 2rem 0;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.9rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.list-item:hover { background: var(--color-hover); }

.item-icon-box {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.item-name {
  font-weight: 600;
  color: var(--color-text);
}

.item-sub {
  font-size: 0.8rem;
  color: var(--color-hint);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chevron {
  color: var(--color-hint);
  font-size: 1.2rem;
}

.icon-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.icon-wrapper {
  position: relative;
  cursor: pointer;
  display: inline-block;
}

.icon-preview {
  font-size: 3.5rem;
  line-height: 1;
  padding: 0.5rem;
  border-radius: 16px;
  background: var(--color-hover);
  border: 2px dashed var(--color-border);
  transition: border-color 0.2s;
  min-width: 4.5rem;
  min-height: 4.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-wrapper:hover .icon-preview { border-color: var(--color-accent); }

.edit-badge {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: var(--color-surface);
  border-radius: 50%;
  font-size: 0.9rem;
  line-height: 1;
  padding: 2px;
}

.hint {
  font-size: 0.8rem;
  color: var(--color-hint);
  margin: 0;
  text-align: center;
  max-width: 280px;
}

.clear-icon-btn {
  border: none;
  background: transparent;
  color: var(--color-accent);
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0.25rem;
}

.picker-container {
  width: 100%;
  max-width: 352px;
  max-height: 360px;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.picker-tabs {
  display: flex;
  gap: 0.35rem;
  padding: 0.15rem;
  background: var(--color-hover);
  border-radius: 10px;
}

.picker-tab {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--color-hint);
  padding: 0.45rem 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}

.picker-tab.active {
  background: var(--color-surface);
  color: var(--color-text);
}

.custom-panel {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding: 0.25rem 0 0.5rem;
}

.file-input { display: none; }

.upload-btn {
  border: 1px dashed var(--color-accent);
  background: transparent;
  color: var(--color-accent);
  border-radius: 10px;
  padding: 0.65rem;
  cursor: pointer;
  font-size: 0.95rem;
}

.upload-btn:disabled {
  opacity: 0.6;
  cursor: default;
}

.upload-hint {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-hint);
  text-align: center;
}

.custom-empty {
  text-align: center;
  color: var(--color-hint);
  font-size: 0.85rem;
  padding: 1rem 0;
}

.custom-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.custom-item {
  position: relative;
  aspect-ratio: 1;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: var(--color-hover);
  cursor: pointer;
  padding: 0.35rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-item.selected {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 1px var(--color-accent);
}

.custom-thumb {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.custom-delete {
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 0.7rem;
  color: var(--color-hint);
  line-height: 1;
}

.custom-delete:hover { color: var(--color-danger); }

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.9rem;
}

.form-group label {
  font-size: 0.85rem;
  color: var(--color-hint);
}

.form-group input {
  padding: 0.65rem 0.75rem;
  background: var(--color-hover);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  color: var(--color-text);
  font-size: 0.95rem;
  outline: none;
}

.form-group input:focus { border-color: var(--color-accent); }

.form-actions {
  display: flex;
  gap: 0.6rem;
  margin-top: 0.5rem;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 0.7rem;
  border-radius: 10px;
  font-size: 0.95rem;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--color-accent);
  color: #fff;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: default;
}

.btn-secondary {
  background: var(--color-hover);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-danger {
  width: 100%;
  margin-top: 1rem;
  padding: 0.7rem;
  border-radius: 10px;
  font-size: 0.95rem;
  cursor: pointer;
  border: 1px solid var(--color-danger, #e5484d);
  background: transparent;
  color: var(--color-danger, #e5484d);
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: default;
}
</style>
