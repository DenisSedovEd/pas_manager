<script setup>
import { ref, computed, onMounted } from 'vue'
import { categoryApi } from '../api/category.js'
import {
  customIconApi,
  customIconFileUrl,
  iconDisplayLabel,
  isCustomIcon,
} from '../api/customIcon.js'
import CategoryIcon from './CategoryIcon.vue'
import EmojiPicker from 'vue3-emoji-picker'
import 'vue3-emoji-picker/css'

const props = defineProps(['category', 'parentCategoryId'])
const emit = defineEmits(['save', 'cancel'])

const isLoading = ref(false)
const showPicker = ref(false)
const pickerTab = ref('emoji')
const isEditing = !!props.category?.id
const rootCategories = ref([])
const customIcons = ref([])
const isUploading = ref(false)
const fileInput = ref(null)

const formData = ref({
  id: props.category?.id || null,
  name: props.category?.name || '',
  icon: props.category?.icon || '🌐',
  description: props.category?.description || '',
  parent_id: props.category?.parent_id ?? props.parentCategoryId ?? null,
})

const selectedCustomId = computed(() => {
  if (!isCustomIcon(formData.value.icon)) return null
  return formData.value.icon.slice('custom:'.length)
})

const loadCustomIcons = async () => {
  customIcons.value = await customIconApi.getList()
}

const onSelectEmoji = (emoji) => {
  formData.value.icon = emoji.i
  showPicker.value = false
}

const onSelectCustom = (icon) => {
  formData.value.icon = icon.key
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
      formData.value.icon = icon.fallback_emoji || '📁'
    }
  } catch {
    alert('Ошибка удаления иконки')
  }
}

const parentOptionLabel = (cat) =>
  `${iconDisplayLabel(cat.icon, '🌐')} ${cat.name}`

const handleSave = async () => {
  if (!formData.value.name.trim()) { alert('Введи название категории'); return }
  isLoading.value = true
  try {
    if (isEditing) {
      await categoryApi.update(formData.value.id, formData.value)
    } else {
      await categoryApi.create(formData.value)
    }
    emit('save')
  } catch {
    alert('Ошибка при сохранении')
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  if (isCustomIcon(formData.value.icon)) {
    pickerTab.value = 'custom'
  }
  try {
    rootCategories.value = await categoryApi.getList()
    if (isEditing && formData.value.id) {
      rootCategories.value = rootCategories.value.filter(c => c.id !== formData.value.id)
    }
  } catch {
    // родитель необязателен
  }
  try {
    await loadCustomIcons()
  } catch {
    // галерея подтянется при открытии вкладки
  }
})
</script>

<template>
  <div class="screen">
    <div class="screen-header">
      <h2>{{ isEditing ? 'Редактировать категорию' : 'Новая категория' }}</h2>
    </div>

    <div class="form">
      <div class="icon-section">
        <div class="icon-wrapper" @click="showPicker = !showPicker">
          <div class="icon-preview">
            <CategoryIcon :icon="formData.icon" fallback="🌐" size="xl" />
          </div>
          <div class="edit-badge">{{ showPicker ? '✕' : '⚙️' }}</div>
        </div>
        <p class="hint">Нажми на иконку, чтобы изменить</p>
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
        <input v-model="formData.name" type="text" placeholder="Название категории" />
      </div>

      <div class="form-group">
        <label>Описание (необязательно)</label>
        <input v-model="formData.description" type="text" placeholder="Краткое описание" />
      </div>

      <div class="form-group">
        <label>Родительская категория <span class="hint-text">(необязательно)</span></label>
        <select v-model="formData.parent_id" class="select-field">
          <option :value="null">— Корневая категория —</option>
          <option
            v-for="cat in rootCategories"
            :key="cat.id"
            :value="cat.id"
          >
            {{ parentOptionLabel(cat) }}
          </option>
        </select>
      </div>

      <div class="form-actions">
        <button class="btn-primary" :disabled="isLoading" @click="handleSave">
          {{ isLoading ? 'Сохранение...' : (isEditing ? 'Обновить' : 'Создать') }}
        </button>
        <button class="btn-secondary" @click="$emit('cancel')">Отмена</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.icon-section { display: flex; flex-direction: column; align-items: center; gap: 0.4rem; }
.icon-wrapper { position: relative; cursor: pointer; display: inline-block; }

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

.hint { font-size: 0.8rem; color: var(--color-hint); margin: 0; }
.hint-text { font-size: 0.8rem; color: var(--color-hint); font-weight: normal; }
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

.select-field {
  width: 100%;
  padding: 0.6rem 0.75rem;
  background: var(--color-hover);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  color: var(--color-text);
  font-size: 0.95rem;
  cursor: pointer;
  outline: none;
}

.select-field:focus { border-color: var(--color-accent); }
</style>
