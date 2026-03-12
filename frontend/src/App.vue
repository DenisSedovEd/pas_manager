<script setup>
import {ref, computed, onMounted} from 'vue'
import {useTelegram} from './composables/useTelegram'
import {authApi} from './api/auth.js'

import PlatformList from './components/PlatformList.vue'
import AccountList from './components/AccountList.vue'
import AccountDetail from './components/AccountDetail.vue'
import AccountEditor from './components/AccountEditor.vue'
import PlatformEditor from './components/PlatformEditor.vue'

const {tg, bio, initApp, initData} = useTelegram()

// ==================== НАВИГАЦИЯ ====================
const screenStack = ref([{name: 'menu'}])
const currentScreen = computed(() => screenStack.value[screenStack.value.length - 1].name)
const currentProps = computed(() => screenStack.value[screenStack.value.length - 1].props || {})

const pushScreen = (name, props = {}) => {
  screenStack.value.push({name, props})
  tg.BackButton.show()
  // Скроллим сам контейнер, так как body у нас заблокирован
  const container = document.querySelector('.app-container')
  if (container) container.scrollTo(0, 0)
}

const popScreen = () => {
  if (screenStack.value.length <= 1) {
    tg.BackButton.hide()
    return
  }
  screenStack.value.pop()
  if (screenStack.value.length === 1) tg.BackButton.hide()
}

tg.BackButton.onClick(popScreen)

// ==================== АВТОРИЗАЦИЯ ====================
const isUnlocked = ref(false)
const password = ref('')
const isBioSupported = ref(false)
const isAuthLoading = ref(false)

const authenticateWithBio = () => {
  bio.authenticate({reason: 'Вход в Safe Manager'}, async (success, token) => {
    if (success) {
      try {
        const res = await authApi.unlockWithBiometric(initData, token)
        if (res.ok || res.status === 'success') {
          isUnlocked.value = true
          tg.HapticFeedback.notificationOccurred('success')
        }
      } catch (e) {
        console.error(e)
      }
    }
  })
}

const handleUnlock = async () => {
  if (!password.value || isAuthLoading.value) return
  isAuthLoading.value = true
  try {
    const res = await authApi.unlockWithPassword(initData, password.value)
    if (res.status === 'success' || res.is_unlocked === true) {
      isUnlocked.value = true
      tg.HapticFeedback.notificationOccurred('success')
    } else {
      tg.showAlert("Неверный пароль")
    }
  } catch (e) {
    tg.showAlert("Ошибка связи с сервером")
  } finally {
    isAuthLoading.value = false
  }
}

onMounted(async () => {
  initApp()

  const safeTop = tg.safeAreaInset?.top || 0
  const finalPadding = safeTop > 0 ? safeTop + 20 : 20
  document.documentElement.style.setProperty('--safe-area-top', `${finalPadding}px`)

  if (tg.setHeaderColor) tg.setHeaderColor('bg_color')
  if (tg.setBackgroundColor) tg.setBackgroundColor('bg_color')
  tg.expand()

  bio.init(async () => {
    isBioSupported.value = bio.isInited && bio.isBiometricAvailable
    const status = await authApi.getStatus(initData)
    isUnlocked.value = status.is_unlocked
    if (!isUnlocked.value && isBioSupported.value) {
      const settings = await authApi.getBioSettings(initData)
      if (settings.is_enabled) authenticateWithBio()
    }
  })

  const handleLogout = () => {
    fetch('/pas-manager/v1/main/auth/logout', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({init_data: initData}),
      keepalive: true
    })
  }
  window.addEventListener('pagehide', handleLogout)
  document.addEventListener('click', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      e.target.focus();
    }
  });
})
</script>

<template>
  <div v-if="!isUnlocked" class="lock-screen">
    <div class="lock-card">
      <div class="lock-icon">🔒</div>
      <h2>Safe Manager</h2>
      <div class="lock-input-wrapper">
        <input v-model="password" type="password" class="lock-input" placeholder="Пароль" @keyup.enter="handleUnlock"/>
        <button class="unlock-btn" @click="handleUnlock" :disabled="isAuthLoading">{{
            isAuthLoading ? '...' : '→'
                                                                                   }}
        </button>
      </div>
      <button v-if="isBioSupported" class="bio-btn" @click="authenticateWithBio">Face ID / Touch ID</button>
    </div>
  </div>

  <div v-else class="app-container">
    <div class="content-wrapper">
      <PlatformList v-if="currentScreen === 'menu'" @select-platform="(p) => pushScreen('accounts', { platform: p })"
                    @add-platform="pushScreen('platform_edit')"/>
      <AccountList v-if="currentScreen === 'accounts'" :platformId="currentProps.platform?.id"
                   @select-account="(acc) => pushScreen('account_detail', { account: acc, platform: currentProps.platform })"
                   @add-account="pushScreen('account_edit', { currentPlatform: currentProps.platform })"/>
      <AccountDetail v-if="currentScreen === 'account_detail'" :account="currentProps.account"
                     @edit="(fullAcc) => pushScreen('account_edit', { account: fullAcc, currentPlatform: currentProps.platform })"
                     @deleted="popScreen"/>
      <AccountEditor v-if="currentScreen === 'account_edit'" :account="currentProps.account"
                     :currentPlatform="currentProps.currentPlatform" @save="popScreen" @cancel="popScreen"/>
      <PlatformEditor v-if="currentScreen === 'platform_edit'" :platform="currentProps.platform" @save="popScreen"
                      @cancel="popScreen"/>
    </div>
  </div>
</template>

<style>
body {
  margin: 0;
  background-color: var(--tg-theme-bg-color);
  color: var(--tg-theme-text-color);
  overflow: hidden;
  -webkit-user-select: text !important;
  user-select: text !important;
}

input, textarea {
  -webkit-user-select: text !important;
  user-select: text !important;
  pointer-events: auto !important;
}

.app-container {
  padding-top: var(--safe-area-top, 24px) !important;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  padding: 0 4px;
  margin-top: 15px;
}

.lock-screen {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--tg-theme-bg-color);
}

.lock-card {
  width: 100%;
  max-width: 320px;
  text-align: center;
  padding: 20px;
}

.lock-input-wrapper {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.lock-input {
  flex: 1;
  background: var(--tg-theme-secondary-bg-color);
  border: 1px solid rgba(128, 128, 128, 0.2);
  padding: 14px;
  border-radius: 12px;
  color: var(--tg-theme-text-color);
  font-size: 16px;
}

.unlock-btn {
  width: 52px;
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  border: none;
  border-radius: 12px;
  font-size: 20px;
}

.bio-btn {
  background: none;
  border: 1px solid var(--tg-theme-button-color);
  color: var(--tg-theme-button-color);
  padding: 12px;
  border-radius: 12px;
  width: 100%;
  font-weight: 600;
}
</style>