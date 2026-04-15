<script setup>
import { ref, computed, onMounted } from 'vue'
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

const screenStack = ref([{ name: 'categories' }])
const currentScreen = computed(() => screenStack.value[screenStack.value.length - 1].name)
const currentProps = computed(() => screenStack.value[screenStack.value.length - 1].props || {})
const canGoBack = computed(() => screenStack.value.length > 1)

const pushScreen = (name, props = {}) => {
  screenStack.value.push({ name, props })
  window.scrollTo(0, 0)
}

const popScreen = () => {
  if (screenStack.value.length > 1) screenStack.value.pop()
}

const loadResources = async () => {
  try {
    resources.value = await resourceApi.getList()
    const def = resources.value.find(r => r.resource_name === 'Без площадки')
    if (def) defaultResourceId.value = def.id
    suggestions.value = await accountApi.getSuggestions()
  } catch {
    console.error('Ошибка загрузки ресурсов')
  }
}

const handleAuthenticated = async () => {
  await loadResources()
}

const handleLogout = async () => {
  await logout()
  screenStack.value = [{ name: 'categories' }]
}

onMounted(async () => {
  const active = await checkStatus()
  if (active) await loadResources()
})
</script>

<template>
  <div class="app-shell">
    <Login v-if="!isAuthenticated" @authenticated="handleAuthenticated" />

    <template v-else>
      <header class="app-header">
        <button v-if="canGoBack" class="back-btn" @click="popScreen">← Назад</button>
        <span v-else class="app-title">🔐 Safe Manager</span>
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
          @select-account="acc => pushScreen('account-detail', { account: acc, category: currentProps.category })"
          @add-account="pushScreen('account-editor', { currentCategory: currentProps.category, resources, defaultResourceId, suggestions })"
          @edit-category="cat => pushScreen('category-editor', { category: cat })"
        />

        <AccountDetail
          v-else-if="currentScreen === 'account-detail'"
          :account="currentProps.account"
          :resources="resources"
          :category="currentProps.category"
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
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #f4f4f8; }
</style>

<style scoped>
.app-shell { min-height: 100vh; display: flex; flex-direction: column; }
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: white;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 10;
}
.app-title { font-weight: 600; font-size: 1rem; }
.back-btn {
  background: none;
  border: none;
  font-size: 0.95rem;
  color: #5856d6;
  cursor: pointer;
  padding: 0.2rem 0;
}
.logout-btn {
  background: none;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  padding: 0.3rem 0.7rem;
  font-size: 0.85rem;
  cursor: pointer;
  color: #666;
}
.logout-btn:hover { background: #f4f4f8; }
.app-content {
  background: white;
  max-width: 600px;
  width: 100%;
  margin: 1rem auto;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 16px rgba(0,0,0,0.06);
  flex: 1;
}
@media (max-width: 640px) {
  .app-content { margin: 0; border-radius: 0; box-shadow: none; }
}
</style>

