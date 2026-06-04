<script setup>
import { ref, computed, onMounted } from 'vue'
import draggable from 'vuedraggable'
import { categoryApi } from '../api/category.js'
import { accountApi } from '../api/account.js'

const emit = defineEmits(['select-category', 'add-category'])
const categories = ref([])
const isLoading = ref(true)
const isEditMode = ref(false)

// ── Поиск ──────────────────────────────────────────────────────────────────
const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)
const searchMode = computed(() => searchQuery.value.trim().length > 0)

let searchTimer = null
const handleSearchInput = () => {
  clearTimeout(searchTimer)
  if (!searchQuery.value.trim()) { searchResults.value = []; return }
  searchTimer = setTimeout(runSearch, 300)
}

const runSearch = async () => {
  if (!searchQuery.value.trim()) return
  isSearching.value = true
  try {
    searchResults.value = await accountApi.search(searchQuery.value.trim())
  } catch {
    alert('Ошибка поиска')
  } finally {
    isSearching.value = false
  }
}

const clearSearch = () => { searchQuery.value = ''; searchResults.value = [] }

// ── CRUD ───────────────────────────────────────────────────────────────────
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

    <!-- Поиск -->
    <div class="search-bar">
      <span class="search-icon">🔍</span>
      <input
        v-model="searchQuery"
        type="text"
        class="search-input"
        placeholder="Поиск по всем данным..."
        @input="handleSearchInput"
      />
      <button v-if="searchQuery" class="search-clear" @click="clearSearch">✕</button>
    </div>

    <!-- Режим поиска -->
    <template v-if="searchMode">
      <div v-if="isSearching" class="loading">Поиск...</div>
      <div v-else-if="searchResults.length === 0" class="empty">Ничего не найдено</div>
      <div v-else class="list">
        <div
          v-for="result in searchResults"
          :key="result.account_id"
          class="list-item search-item"
          @click="$emit('select-category', { id: result.category_id, name: result.category_name, icon: result.category_icon, _searchAccount: result })"
        >
          <span class="item-icon">{{ result.category_icon || '🌐' }}</span>
          <div class="item-info">
            <div class="search-breadcrumb">
              <span v-if="result.parent_category_name" class="breadcrumb-part">{{ result.parent_category_name }}</span>
              <span v-if="result.parent_category_name" class="breadcrumb-sep">›</span>
              <span class="breadcrumb-part">{{ result.category_name }}</span>
              <span v-if="result.resource_name" class="breadcrumb-sep">›</span>
              <span v-if="result.resource_name" class="breadcrumb-resource">{{ result.resource_name }}</span>
            </div>
            <span class="item-name">{{ result.login }}</span>
            <span v-if="result.label || result.email" class="item-sub">
              {{ [result.label, result.email].filter(Boolean).join(' · ') }}
            </span>
          </div>
          <span class="chevron">›</span>
        </div>
      </div>
    </template>

    <!-- Обычный режим -->
    <template v-else>
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
              <span class="item-sub">
                <span v-if="cat.children_count > 0">{{ cat.children_count }} подкат. · </span>
                {{ cat.accounts_count }} аккаунтов
              </span>
            </div>
            <button v-if="isEditMode" class="delete-btn" @click.stop="deleteCategory(cat)">🗑️</button>
            <span v-else class="chevron">›</span>
          </div>
        </template>
      </draggable>
    </template>
  </div>
</template>

<style scoped>
.item-icon { font-size: 1.5rem; flex-shrink: 0; color: var(--color-text); }
.item-info { flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.item-name { font-size: 1rem; font-weight: 500; color: var(--color-text); }
.item-sub { font-size: 0.8rem; color: var(--color-hint); }

/* ── Поиск ── */
.search-bar {
  display: flex;
  align-items: center;
  background: var(--color-hover);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0 0.75rem;
  margin: 0 1rem 0.75rem;
  gap: 0.5rem;
}

.search-icon { opacity: 0.5; flex-shrink: 0; }

.search-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  padding: 0.6rem 0;
  font-size: 0.9rem;
  color: var(--color-text);
}

.search-input::placeholder { color: var(--color-hint); }

.search-clear {
  background: none;
  border: none;
  color: var(--color-hint);
  font-size: 0.85rem;
  cursor: pointer;
  padding: 2px 4px;
}

.search-item { cursor: pointer; }

.search-breadcrumb {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-wrap: wrap;
}

.breadcrumb-part {
  font-size: 0.75rem;
  color: var(--color-hint);
  font-weight: 500;
}

.breadcrumb-resource {
  font-size: 0.75rem;
  color: var(--color-accent);
  font-weight: 500;
}

.breadcrumb-sep {
  font-size: 0.75rem;
  color: var(--color-hint);
  opacity: 0.5;
}
</style>
