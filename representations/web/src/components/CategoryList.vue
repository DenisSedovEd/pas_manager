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
.screen { padding: 0; }
.screen-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1rem 0.5rem;
  border-bottom: 1px solid #2c313c;
}
.screen-header h2 { margin: 0; font-size: 1.25rem; color: #abb2bf; }
.header-actions { display: flex; gap: 0.5rem; }
.icon-btn {
  background: none;
  border: 1.5px solid #3e4451;
  border-radius: 8px;
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.15s;
  color: #abb2bf;
}
.icon-btn.primary { border-color: #61afef; color: #61afef; font-weight: bold; }
.icon-btn:hover { background: #2c313c; }
.loading, .empty { padding: 2rem; text-align: center; color: #8f919d; }
.list { padding: 0.5rem 0; }
.list-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  gap: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #2c313c;
  transition: background 0.1s;
}
.list-item:hover { background: #2c313c; }
.drag-handle { cursor: grab; color: #5c6370; font-size: 1.1rem; }
.item-icon { font-size: 1.5rem; flex-shrink: 0; color: #abb2bf; }
.item-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.item-name { font-size: 1rem; font-weight: 500; color: #abb2bf; }
.item-sub { font-size: 0.8rem; color: #8f919d; }
.chevron { color: #5c6370; font-size: 1.2rem; }
.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 0.2rem;
  border-radius: 6px;
  transition: background 0.15s;
}
.delete-btn:hover { background: #3e4451; }
</style>
