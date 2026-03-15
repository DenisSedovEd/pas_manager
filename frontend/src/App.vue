<script setup>
import {ref, computed, onMounted} from 'vue'
import {initTelegramClipboard} from "./utils/clipboard"
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


// ==================== АВТОРИЗАЦИЯ ====================
const isUnlocked = ref(false)
const password = ref('')
const isBioSupported = ref(false)
const isAuthLoading = ref(false)

const authenticateWithBio = async () => {
  try {
    const settings = await authApi.getBioSettings(initData)
    if (!settings.is_enabled) {
      tg.showAlert('Биометрия ещё не привязана. Войдите по паролю — после входа будет предложена привязка Face ID / Touch ID.')
      return
    }
  } catch (e) {
    console.error('Bio settings check error:', e)
    return
  }

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

const offerBiometricSetup = () => {
  if (!isBioSupported.value) return

  tg.showConfirm('Привязать Face ID / Touch ID для быстрого входа?', (agreed) => {
    if (!agreed) return
    bio.requestAccess({reason: 'Привязка биометрии'}, (granted) => {
      if (!granted) return
      // Генерируем токен и сохраняем в secure storage Telegram
      const bioToken = crypto.randomUUID()
      bio.updateBiometricToken(bioToken, async (updated) => {
        if (!updated) return
        try {
          // Бэкенд шифрует master_password этим токеном
          await authApi.enableBiometric(initData, {bio_token: bioToken})
          tg.HapticFeedback.notificationOccurred('success')
          tg.showAlert('Биометрия привязана!')
        } catch (e) {
          console.error('Bio enable error:', e)
          // Откатываем токен из Telegram если бэкенд упал
          bio.updateBiometricToken('')
        }
      })
    })
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

      // Предложить привязку биометрии если поддерживается и ещё не включена
      if (isBioSupported.value) {
        const settings = await authApi.getBioSettings(initData)
        if (!settings.is_enabled) offerBiometricSetup()
      }
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


  // Telegram Mini App ready
  if (tg) {
    tg.ready()
    tg.expand()
  }
  initTelegramClipboard()
  tg?.BackButton?.onClick(popScreen)

  const safeTop = tg?.safeAreaInset?.top || 0
  const finalPadding = safeTop > 0 ? safeTop + 20 : 20

  document.documentElement.style.setProperty('--safe-area-top', `${finalPadding}px`)
  if (tg?.setHeaderColor) tg.setHeaderColor('bg_color')
  if (tg?.setBackgroundColor) tg.setBackgroundColor('bg_color')

  // Запуск clipboard модуля

  // Инициализация биометрии
  bio.init(async () => {
    isBioSupported.value = bio.isInited && bio.isBiometricAvailable
    const status = await authApi.getStatus(initData)
    isUnlocked.value = status.is_unlocked
    if (!isUnlocked.value && isBioSupported.value) {
      const settings = await authApi.getBioSettings(initData)
      if (settings.is_enabled) authenticateWithBio()
    }
  })

  // --- ЗАВЕРШЕНИЕ СЕССИИ ---
  const handleLogout = () => {
    const url = '/pas-manager/v1/main/auth/logout';
    const data = JSON.stringify({init_data: initData});

    if (navigator.sendBeacon) {
      navigator.sendBeacon(url, data);
    } else {
      fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: data,
        keepalive: true
      });
    }
  }
  window.addEventListener('pagehide', handleLogout)
})


</script>

<template>
  <div v-if="!isUnlocked" class="lock-screen">
    <div class="lock-card">
      <div class="lock-icon">🔒</div>
      <h2>Safe Manager</h2>
      <div class="lock-input-wrapper">
        <input v-model="password" type="password" class="lock-input" placeholder="Пароль" @keyup.enter="handleUnlock"/>
        <button class="unlock-btn" @click="handleUnlock" :disabled="isAuthLoading">
          {{ isAuthLoading ? '...' : '→' }}
        </button>
      </div>
      <button v-if="isBioSupported" class="bio-btn" @click="authenticateWithBio">Face ID / Touch ID</button>
    </div>
  </div>

  <div v-else class="app-container">
    <div class="content-wrapper">
      <PlatformList v-if="currentScreen === 'menu'" @select-platform="(p) => pushScreen('accounts', { platform: p })"
                    @add-platform="pushScreen('platform_edit')"/>
      <AccountList
          v-if="currentScreen === 'accounts'"
          :platformId="currentProps.platform?.id"
          :platform="currentProps.platform"
          @select-account="(acc) => pushScreen('account_detail', { account: acc, platform: currentProps.platform })"
          @add-account="pushScreen('account_edit', { currentPlatform: currentProps.platform })"
          @edit-platform="(p) => pushScreen('platform_edit', { platform: p })"
      />
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
}

input, textarea {
  -webkit-user-select: text !important;
  -webkit-touch-callout: default !important;
  user-select: text !important;
  pointer-events: auto !important;
  z-index: 10;
  position: relative;
  caret-color: var(--tg-theme-button-color, #248bcf) !important;
}

input:focus, textarea:focus {
  outline: none !important;
  box-shadow: 0 0 0 1px var(--tg-theme-button-color);
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
  outline: none;
}

.unlock-btn {
  width: 52px;
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  border: none;
  border-radius: 12px;
  font-size: 20px;
  cursor: pointer;
}

.bio-btn {
  background: none;
  border: 1px solid var(--tg-theme-button-color);
  color: var(--tg-theme-button-color);
  padding: 12px;
  border-radius: 12px;
  width: 100%;
  font-weight: 600;
  cursor: pointer;
}

/* ─── Shared utilities ─── */

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--tg-theme-hint-color);
  border-top-color: var(--tg-theme-button-color);
  border-radius: 50%;
  margin: 0 auto 12px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.status-msg,
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--tg-theme-hint-color);
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.main-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.add-button {
  border: 1px dashed var(--tg-theme-button-color);
  background: transparent;
  margin-top: 8px;
}

.add-icon {
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  font-weight: bold;
}

.add-button .name {
  color: var(--tg-theme-button-color);
  font-weight: 600;
  font-size: 15px;
}

.add-button .description {
  font-size: 11px;
  color: var(--tg-theme-hint-color);
}

/* ─── Shared card item (platform-item, account-item) ─── */

.card-item {
  position: relative;
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  padding: 10px;
  gap: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: rgba(0, 0, 0, 0.08);
  user-select: none;
  -webkit-user-select: none;
}

.card-item:active {
  transform: scale(0.98);
  opacity: 0.8;
}

.card-item.editing {
  cursor: default;
  touch-action: pan-y;
}

.card-item.editing:active {
  transform: none;
  opacity: 1;
}

/* ─── Shared swipe-to-delete ─── */

.swipe-wrapper {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
}

.delete-bg {
  position: absolute;
  inset: 0;
  background: var(--tg-theme-bg-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 20px;
  gap: 6px;
  color: var(--tg-theme-hint-color);
  font-weight: 600;
  pointer-events: none;
  transition: background 0.2s ease, color 0.2s ease;
}

.delete-bg.delete-ready {
  background: #ff3b30;
  color: #fff;
}

.delete-icon {
  font-size: 18px;
}

/* ─── Shared edit-mode & drag ─── */

.edit-mode-btn {
  background: none;
  border: none;
  color: var(--tg-theme-button-color);
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.drag-handle {
  padding: 0 8px 0 4px;
  color: var(--tg-theme-hint-color);
  font-size: 20px;
  cursor: grab;
  user-select: none;
  touch-action: none;
  -webkit-tap-highlight-color: transparent;
}

/* ─── Drag-and-drop (SortableJS) ─── */
/* ВАЖНО: .sortable-fallback ПОСЛЕ .ghost-card — порядок критичен! */

.sortable-fallback {
  opacity: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.ghost-card {
  background: var(--tg-theme-secondary-bg-color) !important;
  color: var(--tg-theme-text-color) !important;
  border-radius: 12px !important;
  opacity: 0.95 !important;
  transform: scale(1.03) !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25) !important;
  z-index: 9999 !important;
  pointer-events: none !important;
  border: 1px solid var(--tg-theme-hint-color) !important;
}

</style>