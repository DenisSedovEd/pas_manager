<script setup>
import { ref } from 'vue'
import { resourceApi } from '../api/resource.js'
import CustomFieldsEditor from './CustomFieldsEditor.vue'

const emit = defineEmits(['save', 'cancel'])

const isLoading = ref(false)
const customFieldsRef = ref(null)
const formData = ref({
  resource_name: '',
  description: '',
})

const handleSave = async () => {
  if (!formData.value.resource_name.trim()) {
    alert('Введи название площадки')
    return
  }
  if (customFieldsRef.value && !customFieldsRef.value.validate()) return
  isLoading.value = true
  try {
    const created = await resourceApi.create({
      resource_name: formData.value.resource_name.trim(),
      description: formData.value.description || null,
    })
    if (customFieldsRef.value) {
      await customFieldsRef.value.save(created.id)
    }
    emit('save', created)
  } catch (err) {
    if (err?.message !== 'validation') alert('Ошибка при сохранении')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="modal-backdrop" @click.self="$emit('cancel')">
    <div class="modal-card">
      <div class="modal-header">
        <h3>Новая площадка</h3>
        <button type="button" class="close-btn" @click="$emit('cancel')">✕</button>
      </div>
      <div class="form">
        <div class="form-group">
          <label>Название *</label>
          <input v-model="formData.resource_name" type="text" placeholder="Например: GitHub" />
        </div>
        <div class="form-group">
          <label>Описание (необязательно)</label>
          <input v-model="formData.description" type="text" placeholder="Краткое описание" />
        </div>
        <CustomFieldsEditor
          ref="customFieldsRef"
          entity-type="resource"
          :entity-id="null"
        />
        <div class="form-actions">
          <button class="btn-primary" :disabled="isLoading" @click="handleSave">
            {{ isLoading ? 'Сохранение...' : 'Добавить' }}
          </button>
          <button class="btn-secondary" @click="$emit('cancel')">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 1000;
}
.modal-card {
  width: min(100%, 480px);
  max-height: 90vh;
  overflow-y: auto;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 1.25rem;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.modal-header h3 { margin: 0; }
.close-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  color: var(--color-text);
}
</style>
