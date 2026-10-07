<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useWebAuth } from './composables/useWebAuth.js'
import { resourceApi } from './api/resource.js'
import { accountApi } from './api/account.js'

import Login from './components/Login.vue'
import CategoryList from './components/CategoryList.vue'
import AccountList from './components/AccountList.vue'
import AccountDetail from './components/AccountDetail.vue'
import AccountEditor from './components/AccountEditor.vue'
import CategoryEditor from './components/CategoryEditor.vue'

const { isAuthenticated, logout, checkStatus } = useWebAuth()

const resources = ref([])
const defaultResourceId = ref(null)
const suggestions = ref({ login: [], email: [], phone: [], label: [] })
const isAppReady = ref(false)
const loadError = ref('')

const selectedCategory = ref(null)
const selectedAccount = ref(null)
const selectedAccountCategory = ref(null)

const col1Mode = ref('list')
const col2Mode = ref('list')
const categoryEditorProps = ref({})
const accountEditorProps = ref({})

const categoryListKey = ref(0)
const accountListKey = ref(0)
const accountDetailKey = ref(0)

const showAccountsColumn = computed(() =>
  !!selectedCategory.value || col2Mode.value !== 'list'
)
const showDetailColumn = computed(() =>
  !!selectedAccount.value
  && col2Mode.value === 'list'
  && !!selectedCategory.value
)

let initRequestId = 0

const loadResources = async () => {
  const [loadedResources, loadedSuggestions] = await Promise.all([
    resourceApi.getList(),
    accountApi.getSuggestions(),
  ])

  resources.value = loadedResources
  suggestions.value = loadedSuggestions

  const def = loadedResources.find(r => r.resource_name === 'Без площадки')
  defaultResourceId.value = def?.id || null
}

const initializeApp = async () => {
  const requestId = ++initRequestId
  isAppReady.value = false
  loadError.value = ''
  try {
    await loadResources()
  } catch (error) {
    if (requestId !== initRequestId) return
    console.error('Ошибка загрузки ресурсов после входа:', error)
    loadError.value = 'Не удалось загрузить данные. Попробуйте обновить страницу.'
  } finally {
    if (requestId !== initRequestId) return
    isAppReady.value = true
  }
}

const resetNavigation = () => {
  selectedCategory.value = null
  selectedAccount.value = null
  selectedAccountCategory.value = null
  col1Mode.value = 'list'
  col2Mode.value = 'list'
  categoryEditorProps.value = {}
  accountEditorProps.value = {}
}

const handleLogout = async () => {
  await logout()
  isAppReady.value = false
  loadError.value = ''
  resources.value = []
  defaultResourceId.value = null
  suggestions.value = { login: [], email: [], phone: [], label: [] }
  resetNavigation()
}

const selectCategory = (cat) => {
  if (col1Mode.value !== 'list') return
  if (cat._searchAccount) {
    const category = {
      id: cat.id,
      name: cat.name,
      icon: cat.icon,
    }
    selectedCategory.value = category
    selectedAccount.value = { id: cat._searchAccount.account_id }
    selectedAccountCategory.value = category
    col2Mode.value = 'list'
    accountDetailKey.value += 1
    return
  }
  selectedCategory.value = cat
  selectedAccount.value = null
  selectedAccountCategory.value = null
  col2Mode.value = 'list'
}

const closeAccountsColumn = () => {
  selectedCategory.value = null
  selectedAccount.value = null
  selectedAccountCategory.value = null
  col2Mode.value = 'list'
  accountEditorProps.value = {}
}

const selectAccount = (acc, cat = null) => {
  if (col2Mode.value !== 'list') return
  selectedAccount.value = acc
  selectedAccountCategory.value = cat || selectedCategory.value
  accountDetailKey.value += 1
}

const closeDetailColumn = () => {
  selectedAccount.value = null
  selectedAccountCategory.value = null
}

const openCategoryEditorInCol1 = (props = {}) => {
  categoryEditorProps.value = props
  col1Mode.value = 'category-editor'
}

const openCategoryEditorInCol2 = (props = {}) => {
  categoryEditorProps.value = props
  col2Mode.value = 'category-editor'
  selectedAccount.value = null
  selectedAccountCategory.value = null
}

const openAccountEditor = (props = {}) => {
  accountEditorProps.value = props
  col2Mode.value = 'account-editor'
  if (!selectedCategory.value && props.currentCategory) {
    selectedCategory.value = props.currentCategory
  }
}

const cancelCategoryEditorCol1 = () => {
  col1Mode.value = 'list'
  categoryEditorProps.value = {}
}

const cancelCategoryEditorCol2 = () => {
  col2Mode.value = 'list'
  categoryEditorProps.value = {}
}

const cancelAccountEditor = () => {
  col2Mode.value = 'list'
  accountEditorProps.value = {}
}

const syncSelectedCategory = (saved) => {
  if (!saved?.id || !selectedCategory.value) return
  if (String(saved.id) !== String(selectedCategory.value.id)) return
  selectedCategory.value = {
    ...selectedCategory.value,
    ...saved,
    name: saved.name ?? selectedCategory.value.name,
    icon: saved.icon ?? selectedCategory.value.icon,
    description: saved.description ?? selectedCategory.value.description,
  }
}

const onCategorySavedCol1 = (saved) => {
  syncSelectedCategory(saved)
  col1Mode.value = 'list'
  categoryEditorProps.value = {}
  categoryListKey.value += 1
  if (selectedCategory.value) {
    accountListKey.value += 1
  }
}

const onCategorySavedCol2 = (saved) => {
  syncSelectedCategory(saved)
  col2Mode.value = 'list'
  categoryEditorProps.value = {}
  categoryListKey.value += 1
  accountListKey.value += 1
}

const onAccountSaved = (payload = {}) => {
  const editedId = accountEditorProps.value.account?.id || null
  const wasSelected = editedId && selectedAccount.value?.id === editedId
  col2Mode.value = 'list'
  accountEditorProps.value = {}
  accountListKey.value += 1
  categoryListKey.value += 1
  if (payload.deleted || !editedId) {
    if (wasSelected || !editedId) {
      selectedAccount.value = null
      selectedAccountCategory.value = null
    }
    return
  }
  if (wasSelected) {
    accountDetailKey.value += 1
  }
}

onMounted(async () => {
  const active = await checkStatus()
  if (!active) {
    isAppReady.value = false
    return
  }

  await initializeApp()
})

watch(
  isAuthenticated,
  async (authenticated, wasAuthenticated) => {
    if (!authenticated) return
    if (wasAuthenticated === authenticated && isAppReady.value) return
    await initializeApp()
  }
)
</script>

<template>
  <div class="app-shell">
    <Login v-if="!isAuthenticated" />

    <div v-else-if="!isAppReady" class="app-loading">
      <div class="app-loading-card">
        <div class="app-loading-spinner"></div>
        <p>{{ loadError || 'Загрузка данных...' }}</p>
      </div>
    </div>

    <template v-else>
      <header class="app-header">
        <div class="header-brand">
          <span class="app-title">🔐 Safe Manager</span>
          <a class="local-link" href="http://192.168.10.1:8000" target="_blank" rel="noopener">local</a>
        </div>
        <button class="logout-btn" @click="handleLogout">Выйти</button>
      </header>

      <main class="app-columns-shell">
        <div class="app-columns">
          <!-- Колонка 1: категории -->
          <section class="app-column">
            <CategoryEditor
              v-if="col1Mode === 'category-editor'"
              :key="'cat-ed-1-' + (categoryEditorProps.category?.id || 'new')"
              :category="categoryEditorProps.category"
              :parent-category-id="categoryEditorProps.parentCategoryId || null"
              @save="onCategorySavedCol1"
              @cancel="cancelCategoryEditorCol1"
            />
            <CategoryList
              v-else
              :key="'cats-' + categoryListKey"
              :selected-category-id="selectedCategory?.id"
              @select-category="selectCategory"
              @add-category="openCategoryEditorInCol1({})"
              @add-account="openAccountEditor({ resources, defaultResourceId, suggestions })"
              @category-deleted="id => {
                if (String(selectedCategory?.id) === String(id)) closeAccountsColumn()
              }"
            />
          </section>

          <!-- Колонка 2: аккаунты / редакторы -->
          <section v-if="showAccountsColumn" class="app-column" :key="'col2-' + (selectedCategory?.id || 'editor')">
            <AccountEditor
              v-if="col2Mode === 'account-editor'"
              :key="'acc-ed-' + (accountEditorProps.account?.id || 'new')"
              :account="accountEditorProps.account"
              :current-category="accountEditorProps.currentCategory"
              :resources="resources"
              :default-resource-id="defaultResourceId"
              :suggestions="suggestions"
              @save="onAccountSaved"
              @cancel="cancelAccountEditor"
              @resource-created="r => resources.push(r)"
            />
            <CategoryEditor
              v-else-if="col2Mode === 'category-editor'"
              :key="'cat-ed-2-' + (categoryEditorProps.category?.id || 'new') + '-' + (categoryEditorProps.parentCategoryId || '')"
              :category="categoryEditorProps.category"
              :parent-category-id="categoryEditorProps.parentCategoryId || null"
              @save="onCategorySavedCol2"
              @cancel="cancelCategoryEditorCol2"
            />
            <AccountList
              v-else-if="selectedCategory"
              :key="'accs-' + accountListKey + '-' + selectedCategory.id"
              :category-id="selectedCategory.id"
              :category="selectedCategory"
              :resources="resources"
              :selected-account-id="selectedAccount?.id"
              @go-back="closeAccountsColumn"
              @select-account="selectAccount"
              @add-account="openAccountEditor({ currentCategory: selectedCategory, resources, defaultResourceId, suggestions })"
              @add-category="openCategoryEditorInCol2({ parentCategoryId: selectedCategory.id })"
              @edit-category="cat => {
                if (String(cat.id) === String(selectedCategory.id)) {
                  openCategoryEditorInCol1({ category: cat })
                } else {
                  openCategoryEditorInCol2({ category: cat })
                }
              }"
              @account-deleted="id => {
                if (String(selectedAccount?.id) === String(id)) closeDetailColumn()
              }"
            />
          </section>

          <!-- Колонка 3: деталь аккаунта -->
          <section v-if="showDetailColumn" class="app-column">
            <AccountDetail
              :key="'det-' + accountDetailKey + '-' + selectedAccount.id"
              :account="selectedAccount"
              :resources="resources"
              :category="selectedAccountCategory || selectedCategory"
              @go-back="closeDetailColumn"
              @edit="acc => openAccountEditor({ account: acc, currentCategory: selectedAccountCategory || selectedCategory, resources, defaultResourceId, suggestions })"
              @deleted="() => { closeDetailColumn(); accountListKey += 1; categoryListKey += 1 }"
            />
          </section>
        </div>
      </main>
    </template>
  </div>
</template>

<style>
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: var(--color-bg); color: var(--color-text); }

.app-shell { min-height: 100vh; background: var(--color-bg); }

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-deep);
  color: var(--color-text);
  position: sticky;
  top: 0;
  z-index: 10;
}

.app-title {
  color: var(--color-accent);
  font-weight: 600;
  font-size: 1rem;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.local-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  border: 1.5px solid var(--color-border);
  border-radius: 10px;
  padding: 0.4rem 0.8rem;
  color: var(--color-text);
  font-size: 0.9rem;
  text-decoration: none;
  transition: background 0.15s;
}

.local-link:hover {
  background: var(--color-hover);
}

.logout-btn {
  background: none;
  border: 1.5px solid var(--color-border);
  border-radius: 10px;
  padding: 0.4rem 0.9rem;
  font-size: 0.9rem;
  cursor: pointer;
  color: var(--color-text);
}

.logout-btn:hover { background: var(--color-hover); }

.app-columns-shell {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: stretch;
  padding: 1rem;
  overflow-x: auto;
  min-height: 0;
}

.app-columns {
  display: flex;
  gap: 14px;
  align-items: stretch;
  margin: 0 auto;
}

.app-column {
  width: 420px;
  min-width: 320px;
  max-width: 420px;
  background: var(--color-surface);
  border: 1px solid var(--color-border-deep);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 5.5rem);
  animation: column-in 0.32s cubic-bezier(0.22, 1, 0.36, 1);
}

.app-column > .screen {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

@keyframes column-in {
  from { opacity: 0; transform: translateX(24px) scale(0.98); }
  to { opacity: 1; transform: none; }
}

.app-loading {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.app-loading-card {
  width: 100%;
  max-width: 320px;
  padding: 1.5rem;
  border: 1px solid var(--color-border-deep);
  border-radius: 16px;
  background: var(--color-surface);
  color: var(--color-text);
  text-align: center;
}

.app-loading-spinner {
  width: 28px;
  height: 28px;
  margin: 0 auto 0.75rem;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: app-spin 0.8s linear infinite;
}

@keyframes app-spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 720px) {
  .app-columns-shell { padding: 0.5rem; }
  .app-column {
    width: min(92vw, 420px);
    min-width: min(92vw, 320px);
    border-radius: 14px;
    box-shadow: none;
    max-height: calc(100vh - 4.5rem);
  }
}
</style>

<style scoped>
.app-shell { min-height: 100vh; display: flex; flex-direction: column; }
@media (max-width: 640px) {
  .app-columns-shell { padding: 0; }
  .app-columns { gap: 0; }
  .app-column {
    border-radius: 0;
    box-shadow: none;
    max-height: calc(100vh - 3.5rem);
  }
}
</style>
