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
const suggestions = ref({ email: [], phone: [], label: [] })
const isAppReady = ref(false)
const loadError = ref('')

const screenStack = ref([{ name: 'categories' }])
const currentScreen = computed(() => screenStack.value[screenStack.value.length - 1].name)
const currentProps = computed(() => screenStack.value[screenStack.value.length - 1].props || {})

let initRequestId = 0
const pushScreen = (name, props = {}) => {
  screenStack.value.push({ name, props })
  window.scrollTo(0, 0)
}

const popScreen = () => {
  if (screenStack.value.length > 1) screenStack.value.pop()
}

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

const handleLogout = async () => {
  await logout()
  isAppReady.value = false
  loadError.value = ''
  resources.value = []
  defaultResourceId.value = null
  suggestions.value = { email: [], phone: [], label: [] }
  screenStack.value = [{ name: 'categories' }]
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
        <span class="app-title">🔐 Safe Manager</span>
        <button class="logout-btn" @click="handleLogout">Выйти</button>
      </header>

      <main class="app-content">
        <CategoryList
          v-if="currentScreen === 'categories'"
          @select-category="cat => pushScreen('accounts', { category: cat, categoryId: cat.id })"
          @add-category="pushScreen('category-editor', {})"
        />

        <AccountList
          v-else-if="currentScreen === 'accounts'"
          :category-id="currentProps.categoryId"
          :category="currentProps.category"
          :resources="resources"
          @go-back="popScreen"
          @select-account="acc => pushScreen('account-detail', { account: acc, category: currentProps.category })"
          @add-account="pushScreen('account-editor', { currentCategory: currentProps.category, resources, defaultResourceId, suggestions })"
          @edit-category="cat => pushScreen('category-editor', { category: cat })"
        />

        <AccountDetail
          v-else-if="currentScreen === 'account-detail'"
          :account="currentProps.account"
          :resources="resources"
          :category="currentProps.category"
          @go-back="popScreen"
          @edit="acc => pushScreen('account-editor', { account: acc, currentCategory: currentProps.category, resources, defaultResourceId, suggestions })"
          @deleted="popScreen"
        />

        <AccountEditor
          v-else-if="currentScreen === 'account-editor'"
          :account="currentProps.account"
          :current-category="currentProps.currentCategory"
          :resources="resources"
          :default-resource-id="defaultResourceId"
          :suggestions="suggestions"
          @save="popScreen"
          @cancel="popScreen"
          @resource-created="r => resources.push(r)"
        />

        <CategoryEditor
          v-else-if="currentScreen === 'category-editor'"
          :category="currentProps.category"
          @save="popScreen"
          @cancel="popScreen"
        />
      </main>
    </template>
  </div>
</template>

<style>
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #282c34; color: #abb2bf; }

.app-shell { min-height: 100vh; background: #282c34; }

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  background: #21252b;
  border-bottom: 1px solid #181a1f;
  color: #abb2bf;
  position: sticky;
  top: 0;
  z-index: 10;
}

.app-title {
  color: #61afef;
  font-weight: 600;
  font-size: 1rem;
}

.logout-btn {
  background: none;
  border: 1.5px solid #3e4451;
  border-radius: 10px;
  padding: 0.4rem 0.9rem;
  font-size: 0.9rem;
  cursor: pointer;
  color: #abb2bf;
}

.logout-btn:hover {
  background: #2c313c;
}

.app-content {
  background: #21252b;
  max-width: 420px;
  width: 100%;
  margin: 1rem auto;
  border: 1px solid #181a1f;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.35);
  flex: 1;
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
  border: 1px solid #181a1f;
  border-radius: 16px;
  background: #21252b;
  color: #abb2bf;
  text-align: center;
}

.app-loading-spinner {
  width: 28px;
  height: 28px;
  margin: 0 auto 0.75rem;
  border: 3px solid #3e4451;
  border-top-color: #61afef;
  border-radius: 50%;
  animation: app-spin 0.8s linear infinite;
}

@keyframes app-spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 720px) {
  .app-content { margin: 0.5rem; border-radius: 14px; box-shadow: none; }
}
</style>

<style scoped>
.app-shell { min-height: 100vh; display: flex; flex-direction: column; }
@media (max-width: 640px) {
  .app-content { margin: 0; border-radius: 0; box-shadow: none; }
}
</style>

