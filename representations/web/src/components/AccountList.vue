<script setup>
import { ref, computed, onMounted } from 'vue'
import draggable from 'vuedraggable'
import { accountApi } from '../api/account.js'

const props = defineProps({
  categoryId: String,
  category: Object,
  resources: { type: Array, default: () => [] },
})
const emit = defineEmits(['select-account', 'add-account', 'edit-category'])

const accounts = ref([])
const isLoading = ref(true)
const isEditMode = ref(false)

const resourceMap = computed(() =>
  Object.fromEntries(props.resources.map(r => [r.id, r]))
)

const fetchAccounts = async () => {
  try {
    const response = await accountApi.getList(props.categoryId)
    accounts.value = response.data || response
  } catch {
    alert('Ошибка загрузки аккаунтов')
  } finally {
    isLoading.value = false
  }
}

const handleReorder = async () => {
  try {
    const ids = accounts.value.map(a => String(a.id))
    await accountApi.reorder(ids)
  } catch {
    await fetchAccounts()
  }
}

const deleteAccount = async (account) => {
  if (!confirm(`Удалить аккаунт «${account.label || account.login}»?`)) return
  try {
    await accountApi.delete(account.id)
    accounts.value = accounts.value.filter(a => a.id !== account.id)
  } catch {
    alert('Ошибка удаления')
  }
}

const getResourceName = (account) => {
  return resourceMap.value[account.resource_id]?.resource_name || 'Без площадки'
}

onMounted(fetchAccounts)
</script>

<template>
  <div class="screen">
    <div class="screen-header">
      <h2>{{ category?.icon || '📁' }} {{ category?.name }}</h2>
      <div class="header-actions">
        <button v-if="!isEditMode" class="icon-btn" @click="$emit('edit-category', category)" title="Редактировать категорию">⚙️</button>
        <button v-if="isEditMode" class="icon-btn" @click="isEditMode = false">✅</button>
        <button v-else class="icon-btn" @click="isEditMode = true">✏️</button>
        <button class="icon-btn primary" @click="$emit('add-account')">＋</button>
      </div>
    </div>

    <div v-if="isLoading" class="loading">Загрузка...</div>
    <div v-else-if="!accounts.length" class="empty">Нет аккаунтов. Добавь первый!</div>

    <draggable
      v-else
      v-model="accounts"
      item-key="id"
      handle=".drag-handle"
      @end="handleReorder"
      class="list"
    >
      <template #item="{ element: acc }">
        <div class="list-item" @click="!isEditMode && $emit('select-account', acc)">
          <span v-if="isEditMode" class="drag-handle">☰</span>
          <span class="item-icon">🔑</span>
          <div class="item-info">
            <span class="item-name">{{ acc.label || acc.login }}</span>
            <span class="item-sub">{{ getResourceName(acc) }}</span>
          </div>
          <button v-if="isEditMode" class="delete-btn" @click.stop="deleteAccount(acc)">🗑️</button>
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
  border-bottom: 1px solid #eee;
}
.screen-header h2 { margin: 0; font-size: 1.25rem; }
.header-actions { display: flex; gap: 0.5rem; }
.icon-btn {
  background: none;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  font-size: 1rem;
}
.icon-btn.primary { border-color: #5856d6; color: #5856d6; font-weight: bold; }
.icon-btn:hover { background: #f0f0f0; }
.loading, .empty { padding: 2rem; text-align: center; color: #999; }
.list { padding: 0.5rem 0; }
.list-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  gap: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.1s;
}
.list-item:hover { background: #fafafa; }
.drag-handle { cursor: grab; color: #bbb; font-size: 1.1rem; }
.item-icon { font-size: 1.4rem; flex-shrink: 0; }
.item-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.item-name { font-size: 1rem; font-weight: 500; }
.item-sub { font-size: 0.8rem; color: #888; }
.chevron { color: #bbb; font-size: 1.2rem; }
.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 0.2rem;
  border-radius: 6px;
}
.delete-btn:hover { background: #ffe5e5; }
</style>
