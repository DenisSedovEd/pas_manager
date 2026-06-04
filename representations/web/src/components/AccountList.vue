<script setup>
import { ref, computed, onMounted } from 'vue'
import draggable from 'vuedraggable'
import { accountApi } from '../api/account.js'
import { categoryApi } from '../api/category.js'

const props = defineProps({
  categoryId: String,
  category: Object,
  resources: { type: Array, default: () => [] },
})
const emit = defineEmits(['select-account', 'add-account', 'edit-category', 'go-back', 'select-subcategory'])

const accounts = ref([])
const subcategories = ref([])
const isLoading = ref(true)
const isEditMode = ref(false)

const resourceMap = computed(() =>
  Object.fromEntries(props.resources.map(r => [r.id, r]))
)

const fetchAccounts = async () => {
  try {
    const [accountsResp, childrenResp] = await Promise.all([
      accountApi.getList(props.categoryId),
      categoryApi.getChildren(props.categoryId),
    ])
    accounts.value = accountsResp.data || accountsResp
    subcategories.value = childrenResp.data || childrenResp
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

const deleteSubcategory = async (sub) => {
  if (!confirm(`Удалить категорию «${sub.icon || ''} ${sub.name}»?`)) return
  try {
    await categoryApi.delete(sub.id)
    subcategories.value = subcategories.value.filter(s => s.id !== sub.id)
  } catch {
    alert('Ошибка удаления категории')
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

    <template v-else>
      <!-- Подкатегории -->
      <div v-if="subcategories.length > 0" class="subcategories-section">
        <div class="section-label">Подкатегории</div>
        <div
          v-for="sub in subcategories"
          :key="sub.id"
          class="list-item subcategory-item"
          @click="!isEditMode && $emit('select-subcategory', sub)"
        >
          <span class="item-icon">{{ sub.icon || '📁' }}</span>
          <div class="item-info">
            <span class="item-name">{{ sub.name }}</span>
            <span class="item-sub">
              <span v-if="sub.children_count > 0">{{ sub.children_count }} подкат. · </span>
              {{ sub.accounts_count }} аккаунтов
            </span>
          </div>
          <button v-if="isEditMode" class="delete-btn" @click.stop="deleteSubcategory(sub)">🗑️</button>
          <span v-else class="chevron">›</span>
        </div>
        <div v-if="accounts.length > 0" class="section-divider"></div>
      </div>

      <div v-if="!accounts.length && !subcategories.length" class="empty">Нет аккаунтов. Добавь первый!</div>

      <draggable
        v-if="accounts.length > 0"
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
    </template>
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

/* ── Подкатегории ── */
.subcategories-section {
  padding: 0;
}

.section-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-hint);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0.5rem 1rem 0.25rem;
}

.section-divider {
  height: 1px;
  background: var(--color-border);
  margin: 0.5rem 1rem;
}

.subcategory-item {
  cursor: pointer;
}

.item-icon { font-size: 1.5rem; flex-shrink: 0; }
.item-name { font-size: 1rem; font-weight: 500; color: var(--color-text); }
.item-sub { font-size: 0.8rem; color: var(--color-hint); }
</style>
