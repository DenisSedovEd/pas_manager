<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import draggable from 'vuedraggable'
import { accountApi } from '../api/account.js'
import { categoryApi } from '../api/category.js'
import { iconDisplayLabel } from '../api/customIcon.js'
import AddItemMenu from './AddItemMenu.vue'
import CategoryIcon from './CategoryIcon.vue'

const props = defineProps({
  categoryId: String,
  category: Object,
  resources: { type: Array, default: () => [] },
})
const emit = defineEmits(['select-account', 'add-account', 'add-category', 'edit-category', 'go-back'])

const accounts = ref([])
const subcategories = ref([])
const subAccounts = ref({})
const expandedSubIds = ref({})
const subLoadingIds = ref({})
const isLoading = ref(true)
const isEditMode = ref(false)

const resourceMap = computed(() =>
  Object.fromEntries(props.resources.map(r => [r.id, r]))
)

const hasVisibleContent = computed(() =>
  accounts.value.length > 0
  || subcategories.value.length > 0
  || Object.values(subAccounts.value).some(list => list.length > 0)
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

const loadSubAccounts = async (subId, force = false) => {
  if (!force && subAccounts.value[subId]) return
  subLoadingIds.value = { ...subLoadingIds.value, [subId]: true }
  try {
    const resp = await accountApi.getList(subId)
    subAccounts.value = { ...subAccounts.value, [subId]: resp.data || resp }
  } catch {
    alert('Ошибка загрузки аккаунтов подкатегории')
  } finally {
    const next = { ...subLoadingIds.value }
    delete next[subId]
    subLoadingIds.value = next
  }
}

const toggleSubcategory = async (sub) => {
  if (isEditMode.value) return
  const subId = sub.id
  if (expandedSubIds.value[subId]) {
    expandedSubIds.value = { ...expandedSubIds.value, [subId]: false }
    return
  }
  expandedSubIds.value = { ...expandedSubIds.value, [subId]: true }
  await loadSubAccounts(subId)
}

const dragGroup = computed(() => (
  isEditMode.value ? 'accounts' : { name: 'accounts', pull: false, put: false }
))

const getListByCategoryId = (categoryId) => {
  if (String(categoryId) === String(props.categoryId)) return accounts.value
  return subAccounts.value[categoryId] || []
}

const refreshAll = async () => {
  await fetchAccounts()
  for (const sub of subcategories.value) {
    if (expandedSubIds.value[sub.id]) {
      await loadSubAccounts(sub.id, true)
    }
  }
}

const persistOrder = async (categoryId) => {
  const list = getListByCategoryId(categoryId)
  if (!list.length) return
  const ids = list.map(a => String(a.id))
  await accountApi.reorder(ids)
}

const moveAccountToCategory = async (account, targetCategoryId) => {
  if (String(account.category_id) === String(targetCategoryId)) return

  const detail = await accountApi.getDetail(account.id)
  await accountApi.update(account.id, {
    ...detail,
    category_id: String(targetCategoryId),
  })
  account.category_id = String(targetCategoryId)
}

const handleListChange = async (event, targetCategoryId) => {
  if (!isEditMode.value) return

  try {
    if (event.added) {
      await moveAccountToCategory(event.added.element, targetCategoryId)
    }

    if (event.added || event.moved || event.removed) {
      await persistOrder(targetCategoryId)
    }
  } catch {
    alert('Ошибка сохранения')
    await refreshAll()
  }
}

const expandAllSubcategories = async () => {
  const nextExpanded = { ...expandedSubIds.value }
  for (const sub of subcategories.value) {
    nextExpanded[sub.id] = true
    await loadSubAccounts(sub.id)
  }
  expandedSubIds.value = nextExpanded
}

watch(isEditMode, async (enabled) => {
  if (enabled) await expandAllSubcategories()
})

const deleteAccount = async (account, subId = null) => {
  if (!confirm(`Удалить аккаунт «${account.label || account.login}»?`)) return
  try {
    await accountApi.delete(account.id)
    if (subId) {
      subAccounts.value = {
        ...subAccounts.value,
        [subId]: subAccounts.value[subId].filter(a => a.id !== account.id),
      }
    } else {
      accounts.value = accounts.value.filter(a => a.id !== account.id)
    }
  } catch {
    alert('Ошибка удаления')
  }
}

const deleteSubcategory = async (sub) => {
  if (!confirm(`Удалить категорию «${iconDisplayLabel(sub.icon)} ${sub.name}»?`)) return
  try {
    await categoryApi.delete(sub.id)
    subcategories.value = subcategories.value.filter(s => s.id !== sub.id)
    const nextAccounts = { ...subAccounts.value }
    delete nextAccounts[sub.id]
    subAccounts.value = nextAccounts
    const nextExpanded = { ...expandedSubIds.value }
    delete nextExpanded[sub.id]
    expandedSubIds.value = nextExpanded
  } catch {
    alert('Ошибка удаления категории')
  }
}

const getResourceName = (account) => {
  return resourceMap.value[account.resource_id]?.resource_name || '-'
}

const selectAccount = (account, subCategory = null) => {
  if (isEditMode.value) return
  emit('select-account', account, subCategory)
}

onMounted(fetchAccounts)
</script>

<template>
  <div class="screen">
    <div class="screen-header">
      <div class="title-row">
        <button class="sub-back-btn" @click="$emit('go-back')">⬅️</button>
        <h2 class="title-with-icon"><CategoryIcon :icon="category?.icon" fallback="📁" /><span>{{ category?.name }}</span></h2>
      </div>
      <div class="header-actions">
        <button v-if="!isEditMode" class="icon-btn" @click="$emit('edit-category', category)" title="Редактировать категорию">⚙️</button>
        <button v-if="isEditMode" class="icon-btn" @click="isEditMode = false">✅</button>
        <button v-else class="icon-btn" @click="isEditMode = true">✏️</button>
        <AddItemMenu
          @add-account="$emit('add-account')"
          @add-category="$emit('add-category')"
        />
      </div>
    </div>

    <div v-if="isLoading" class="loading">Загрузка...</div>

    <template v-else>
      <div v-if="subcategories.length > 0" class="subcategories-section">
        <div class="section-label">Подкатегории</div>
        <div
          v-for="sub in subcategories"
          :key="sub.id"
          class="subcategory-group"
        >
          <div
            class="list-item subcategory-item"
            :class="{ expanded: expandedSubIds[sub.id] }"
            @click="toggleSubcategory(sub)"
          >
            <CategoryIcon class="item-icon" :icon="sub.icon" fallback="📁" />
            <div class="item-info">
              <span class="item-name">{{ sub.name }}</span>
              <span class="item-sub">{{ sub.accounts_count }} аккаунтов</span>
            </div>
            <div class="subcategory-actions">
              <button
                class="edit-btn"
                title="Редактировать подкатегорию"
                @click.stop="$emit('edit-category', sub)"
              >⚙️</button>
              <button v-if="isEditMode" class="delete-btn" @click.stop="deleteSubcategory(sub)">🗑️</button>
              <span v-else class="chevron expand-chevron" :class="{ open: expandedSubIds[sub.id] }">›</span>
            </div>
          </div>

          <div v-if="expandedSubIds[sub.id]" class="sub-accounts">
            <div v-if="subLoadingIds[sub.id]" class="sub-status">Загрузка...</div>
            <draggable
              v-else
              :model-value="subAccounts[sub.id] || []"
              @update:model-value="(list) => { subAccounts[sub.id] = list }"
              item-key="id"
              handle=".drag-handle"
              :group="dragGroup"
              :disabled="!isEditMode"
              ghost-class="drag-ghost"
              class="sub-accounts-list"
              :class="{ 'drop-target': isEditMode && !(subAccounts[sub.id] || []).length }"
              @change="(event) => handleListChange(event, sub.id)"
            >
              <template #item="{ element: acc }">
                <div class="list-item sub-account-item" @click="selectAccount(acc, sub)">
                  <span v-if="isEditMode" class="drag-handle">☰</span>
                  <div class="item-icon-box"><CategoryIcon :icon="sub.icon" fallback="👤" size="lg" /></div>
                  <div class="item-info">
                    <div class="item-top-row">
                      <span class="item-resource">{{ getResourceName(acc) }}</span>
                      <span v-if="acc.label" class="item-label">{{ acc.label }}</span>
                    </div>
                    <span class="item-login">{{ acc.login }}</span>
                  </div>
                  <button v-if="isEditMode" class="delete-btn" @click.stop="deleteAccount(acc, sub.id)">🗑️</button>
                  <span v-else class="chevron">›</span>
                </div>
              </template>
            </draggable>
            <div
              v-if="isEditMode && !(subAccounts[sub.id] || []).length"
              class="sub-status sub-drop-hint"
            >Перетащи аккаунт сюда</div>
            <div
              v-else-if="!isEditMode && !(subAccounts[sub.id] || []).length"
              class="sub-status"
            >Нет аккаунтов</div>
          </div>
        </div>
      </div>

      <div v-if="!hasVisibleContent && !isEditMode" class="empty">Нет аккаунтов. Добавь первый!</div>

      <draggable
        v-if="isEditMode || accounts.length > 0"
        v-model="accounts"
        item-key="id"
        handle=".drag-handle"
        :group="dragGroup"
        :disabled="!isEditMode"
        ghost-class="drag-ghost"
        class="list"
        :class="{ 'drop-target': isEditMode && accounts.length === 0 }"
        @change="(event) => handleListChange(event, categoryId)"
      >
        <template #item="{ element: acc }">
          <div class="list-item" @click="selectAccount(acc)">
            <span v-if="isEditMode" class="drag-handle">☰</span>
            <div class="item-icon-box"><CategoryIcon :icon="category?.icon" fallback="👤" size="lg" /></div>
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
      <div
        v-if="isEditMode && accounts.length === 0 && (subcategories.length > 0 || hasVisibleContent)"
        class="sub-status root-drop-hint"
      >Перетащи аккаунт сюда</div>
    </template>
  </div>
</template>

<style scoped>
.title-row { display: flex; align-items: center; gap: 0.75rem; }

.title-with-icon { display: inline-flex; align-items: center; gap: 0.5rem; }

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

.subcategories-section:has(~ .list) .subcategory-group:last-child > .subcategory-item {
  border-bottom: none;
}

.subcategory-group {
  border-bottom: none;
}

.subcategory-item {
  cursor: pointer;
}

.subcategory-item.expanded {
  background: var(--color-hover);
}

.subcategory-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
}

.edit-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.2rem 0.35rem;
  opacity: 0.75;
  line-height: 1;
}

.edit-btn:hover {
  opacity: 1;
}

.expand-chevron {
  display: inline-block;
  transition: transform 0.2s ease;
}

.expand-chevron.open {
  transform: rotate(90deg);
}

.sub-accounts {
  background: rgba(0, 0, 0, 0.12);
}

.sub-accounts-list {
  padding: 0;
}

.sub-accounts-list.drop-target {
  min-height: 44px;
}

.list.drop-target {
  min-height: 48px;
}

.sub-drop-hint,
.root-drop-hint {
  color: var(--color-muted);
  font-style: italic;
}

.root-drop-hint {
  padding: 0.65rem 1rem;
}

:global(.drag-ghost) {
  opacity: 0.45;
}

.sub-account-item {
  padding-left: 2.25rem;
  border-bottom: 1px solid var(--color-separator);
}

.sub-account-item:last-child {
  border-bottom: none;
}

.sub-status {
  padding: 0.65rem 1rem 0.65rem 2.25rem;
  font-size: 0.85rem;
  color: var(--color-hint);
}

.item-icon { font-size: 1.5rem; flex-shrink: 0; }
.item-name { font-size: 1rem; font-weight: 500; color: var(--color-text); }
.item-sub { font-size: 0.8rem; color: var(--color-hint); }
</style>
