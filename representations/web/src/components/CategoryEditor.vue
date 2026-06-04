<script setup>
import { ref, onMounted } from 'vue'
import { categoryApi } from '../api/category.js'
import EmojiPicker from 'vue3-emoji-picker'
import 'vue3-emoji-picker/css'

const props = defineProps(['category', 'parentCategoryId'])
const emit = defineEmits(['save', 'cancel'])

const isLoading = ref(false)
const showPicker = ref(false)
const isEditing = !!props.category?.id
const rootCategories = ref([])

const formData = ref({
  id: props.category?.id || null,
  name: props.category?.name || '',
  icon: props.category?.icon || '🌐',
  description: props.category?.description || '',
  parent_id: props.category?.parent_id ?? props.parentCategoryId ?? null,
})

const onSelectEmoji = (emoji) => {
  formData.value.icon = emoji.i
  showPicker.value = false
}

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
  try {
    rootCategories.value = await categoryApi.getList()
    if (isEditing && formData.value.id) {
      rootCategories.value = rootCategories.value.filter(c => c.id !== formData.value.id)
    }
  } catch {
    // игнорируем — родитель необязателен
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
          <div class="icon-preview">{{ formData.icon }}</div>
          <div class="edit-badge">{{ showPicker ? '✕' : '⚙️' }}</div>
        </div>
        <p class="hint">Нажми на иконку, чтобы изменить</p>
        <div v-if="showPicker" class="picker-container">
          <EmojiPicker :native="true" @select="onSelectEmoji" />
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
            {{ cat.icon || '🌐' }} {{ cat.name }}
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
.picker-container { max-height: 300px; overflow: auto; }

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
