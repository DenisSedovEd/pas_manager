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
.title-row { display: flex; align-items: center; gap: 0.75rem; }
.item-icon-box {
  width: 42px;
  height: 42px;
  min-width: 42px;
  background: var(--color-hover);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: var(--color-text);
  flex-shrink: 0;
}
.item-info { flex: 1; display: flex; flex-direction: column; gap: 2px; overflow: hidden; }
.item-top-row { display: flex; align-items: baseline; gap: 6px; white-space: nowrap; overflow: hidden; }
.item-resource { font-size: 15px; font-weight: 600; color: var(--color-text); flex-shrink: 0; }
.item-label { font-size: 12px; color: var(--color-hint); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-login { font-size: 11px; color: var(--color-hint); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>
