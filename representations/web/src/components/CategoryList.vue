<script setup>
import { ref, onMounted } from 'vue'
import draggable from 'vuedraggable'
import { categoryApi } from '../api/category.js'

const emit = defineEmits(['select-category', 'add-category'])
const categories = ref([])
const isLoading = ref(true)
const isEditMode = ref(false)

const fetchCategories = async () => {
  try {
    const response = await categoryApi.getList()
    categories.value = response.data || response
  } catch {
    alert('Ошибка загрузки категорий')
  } finally {
    isLoading.value = false
  }
}

const handleReorder = async () => {
  try {
    const ids = categories.value.map(c => String(c.id))
    await categoryApi.reorder(ids)
  } catch {
    await fetchCategories()
  }
}

const deleteCategory = async (category) => {
  if (!confirm(`Удалить категорию «${category.icon} ${category.name}»?`)) return
  try {
    await categoryApi.delete(category.id)
    categories.value = categories.value.filter(c => c.id !== category.id)
  } catch {
    alert('Ошибка удаления')
  }
}

onMounted(fetchCategories)
</script>

<template>
  <div class="screen">
    <div class="screen-header">
      <h2>Категории</h2>
      <div class="header-actions">
        <button v-if="!isEditMode" class="icon-btn" @click="isEditMode = true" title="Редактировать">⚙️</button>
        <button v-else class="icon-btn" @click="isEditMode = false" title="Готово">✅</button>
        <button class="icon-btn primary" @click="$emit('add-category')" title="Добавить">＋</button>
      </div>
    </div>

    <div v-if="isLoading" class="loading">Загрузка...</div>
    <div v-else-if="!categories.length" class="empty">Нет категорий. Создай первую!</div>

    <draggable
      v-else
      v-model="categories"
      item-key="id"
      handle=".drag-handle"
      @end="handleReorder"
      class="list"
    >
      <template #item="{ element: cat }">
        <div class="list-item" @click="!isEditMode && $emit('select-category', cat)">
          <span v-if="isEditMode" class="drag-handle">☰</span>
          <span class="item-icon">{{ cat.icon || '📁' }}</span>
          <div class="item-info">
            <span class="item-name">{{ cat.name }}</span>
            <span class="item-sub">{{ cat.accounts_count }} аккаунтов</span>
          </div>
          <button v-if="isEditMode" class="delete-btn" @click.stop="deleteCategory(cat)">🗑️</button>
          <span v-else class="chevron">›</span>
        </div>
      </template>
    </draggable>
  </div>
</template>

<style scoped>
.item-icon { font-size: 1.5rem; flex-shrink: 0; color: var(--color-text); }
.item-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.item-name { font-size: 1rem; font-weight: 500; color: var(--color-text); }
.item-sub { font-size: 0.8rem; color: var(--color-hint); }
</style>
