<script setup>
import { ref, computed, onMounted } from 'vue'
import draggable from 'vuedraggable'
import { accountApi } from '../api/account.js'

const props = defineProps({
  categoryId: String,
  category: Object,
  resources: { type: Array, default: () => [] },
})
const emit = defineEmits(['select-account', 'add-account', 'edit-category', 'go-back'])

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
  return resourceMap.value[account.resource_id]?.resource_name || '-'
}

onMounted(fetchAccounts)
</script>

<template>
  <div class="screen">
    <div class="screen-header">
      <div class="title-row">
        <button class="sub-back-btn" @click="$emit('go-back')">⬅️</button>
        <h2>{{ category?.icon || '📁' }} {{ category?.name }}</h2>
      </div>
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
          <div class="item-icon-box">{{ '👤' }}</div>
          <div class="item-info">
            <div class="item-top-row">
              <span class="item-resource">{{ getResourceName(acc) }}</span>
              <span v-if="acc.label" class="item-label">{{ acc.label }}</span>
            </div>
            <span class="item-login">{{ acc.login }}</span>
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
  border-bottom: 1px solid #2c313c;
}
.title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.screen-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #abb2bf;
}
.sub-back-btn {
  border: none;
  background: none;
  color: #61afef;
  font-size: 1.2rem;
  cursor: pointer;
}
.header-actions {
  display: flex;
  gap: 0.5rem;
}
.icon-btn {
  background: none;
  border: 1.5px solid #3e4451;
  border-radius: 8px;
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  font-size: 1rem;
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
.item-icon-box {
  width: 42px;
  height: 42px;
  min-width: 42px;
  background: #2c313c;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #abb2bf;
  flex-shrink: 0;
}
.item-info { flex: 1; display: flex; flex-direction: column; gap: 2px; overflow: hidden; }
.item-top-row { display: flex; align-items: baseline; gap: 6px; white-space: nowrap; overflow: hidden; }
.item-resource { font-size: 15px; font-weight: 600; color: #abb2bf; flex-shrink: 0; }
.item-label { font-size: 12px; color: #8f919d; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-login { font-size: 11px; color: #7c828f; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chevron { color: #5c6370; font-size: 1.2rem; }
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
