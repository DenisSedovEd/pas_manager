<script setup>
import {ref, onMounted} from 'vue';
import {useTelegram} from './composables/useTelegram';
import {authApi} from './api/auth';
import PlatformList from './components/PlatformList.vue';
import AccountList from './components/AccountList.vue';
import AccountEditor from "./components/AccountEditor.vue";

const {tg, bio, initApp, initData} = useTelegram();

const isUnlocked = ref(false);
const password = ref('');
const isBioSupported = ref(false);
const isAuthLoading = ref(false);
const currentScreen = ref('menu');
const selectedPlatform = ref(null);
const editingAccount = ref(null);

onMounted(async () => {
  initApp();

  if (tg.setHeaderColor) tg.setHeaderColor('bg_color');
  if (tg.setBackgroundColor) tg.setBackgroundColor('bg_color');
  tg.expand();

  // 1. Инициализация биометрии
  bio.init(async () => {
    isBioSupported.value = bio.isInited && bio.isBiometricAvailable;

    try {
      const status = await authApi.getStatus(initData);
      isUnlocked.value = status.is_unlocked;
    } catch (e) {
      console.error("Ошибка проверки статуса:", e);
    }
  });

  // 2. ГАРАНТИРОВАННЫЙ ВЫХОД: вызываем логаут при закрытии Mini App
  // Это сработает, когда пользователь нажмет (X) в Telegram
  window.addEventListener('beforeunload', () => {
    navigator.sendBeacon('/pas-manager/main/auth/logout', initData);
  });
});

const handlePasswordUnlock = async () => {
  if (!password.value) return;
  isAuthLoading.value = true;

  try {
    const res = await authApi.unlockWithPassword(initData, password.value);
    if (res.ok) {
      isUnlocked.value = true;
      if (isBioSupported.value && !bio.isBiometricTokenSaved) {
        bio.updateBiometricToken('SECURE_TOKEN');
      }
    } else {
      tg.showAlert("Неверный мастер-пароль");
    }
  } finally {
    isAuthLoading.value = false;
  }
};

const authenticateWithBio = () => {
  bio.authenticate({reason: 'Вход в сейф'}, async (success, token) => {
    if (success) {
      const res = await authApi.unlockWithBiometric(initData, token);
      if (res.ok) isUnlocked.value = true;
    }
  });
};

const onAccountSelect = (account) => {
  editingAccount.value = account;
  currentScreen.value = 'account_details';
};

const onPlatformSelect = (platform) => {
  selectedPlatform.value = platform;
  currentScreen.value = 'accounts';
};

// Функция для возврата назад
const goBack = () => {
  if (currentScreen.value === 'account_details') {
    currentScreen.value = 'accounts';
    editingAccount.value = null;
  } else if (currentScreen.value === 'accounts') {
    currentScreen.value = 'platforms';
  } else {
    currentScreen.value = 'menu';
  }
};

const openMyAccounts = () => {
  currentScreen.value = 'platforms';
};

const openAddAccount = () => {
  currentScreen.value = 'add_account';
};

</script>

<template>
  <div class="app-container">

    <div v-if="!isUnlocked" class="auth-card">
      <div class="logo">🛡️</div>
      <h1>Safe Manager</h1>

      <div class="input-group">
        <input
            v-model="password"
            type="password"
            placeholder="Мастер-пароль"
            @keyup.enter="handlePasswordUnlock"
        />
        <button
            @click="handlePasswordUnlock"
            class="primary-btn"
            :disabled="isAuthLoading"
        >
          {{ isAuthLoading ? 'Вход...' : 'Войти' }}
        </button>
      </div>

      <div v-if="isBioSupported" class="bio-section">
        <div class="divider"><span>или</span></div>
        <button @click="authenticateWithBio" class="bio-btn">
          🧬 Использовать FaceID
        </button>
      </div>
    </div>

    <div v-else class="vault-wrapper">

      <div v-if="currentScreen === 'menu'" class="main-menu">
        <div class="header">
          <h1>Safe Manager</h1>
        </div>

        <div class="menu-grid">
          <button @click="openMyAccounts" class="menu-item">
            <span class="menu-icon">📁</span>
            <span class="menu-label">Мои аккаунты</span>
          </button>

          <button @click="openAddAccount" class="menu-item">
            <span class="menu-icon">➕</span>
            <span class="menu-label">Добавить аккаунт</span>
          </button>
        </div>
      </div>

      <div v-else-if="currentScreen === 'platforms'">
        <div class="header">
          <div class="navigation-row">
            <button @click="goBack" class="back-btn">←</button>
            <h1>Платформы</h1>
          </div>
        </div>
        <PlatformList @select-platform="onPlatformSelect"/>
      </div>

      <div v-else-if="currentScreen === 'accounts'">
        <div class="header">
          <div class="navigation-row">
            <button @click="goBack" class="back-btn">←</button>
            <h1>{{ selectedPlatform?.name }}</h1>
          </div>
        </div>
        <AccountList
            :platform-id="selectedPlatform?.id"
            @select-account="onAccountSelect"
        />
      </div>

      <div v-else-if="currentScreen === 'account_details'">
        <div class="header">
          <div class="navigation-row">
            <button @click="goBack" class="back-btn">←</button>
            <h1>Редактирование</h1>
          </div>
        </div>
        <AccountEditor
            :account="editingAccount"
            :currentPlatform="selectedPlatform"
            @save="goBack"
        />
      </div>

      <div v-else-if="currentScreen === 'add_account'">
        <div class="header">
          <div class="navigation-row">
            <button @click="goBack" class="back-btn">←</button>
            <h1>Новый аккаунт</h1>
          </div>
        </div>
        <AccountEditor @save="goBack"/>
      </div>

    </div>
  </div>
</template>

<style scoped>
:global(body) {
  margin: 0;
  padding: 0;
  background: var(--tg-theme-bg-color);
}

:global(html), :global(body) {
  margin: 0;
  padding: 0;
  background-color: var(--tg-theme-bg-color); /* Принудительно системный цвет */
  color: var(--tg-theme-text-color);
  height: 100%;
  overflow: hidden; /* Основное окно не скроллим */
}

.container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.account-card {
  cursor: pointer;
  transition: background 0.2s;
}

.account-card:active {
  background: var(--tg-theme-bg-color);
}

.arrow {
  color: var(--tg-theme-hint-color);
  font-size: 20px;
}

/* Стили для навигации внутри сейфа */
.vault-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
  min-height: 100vh;
  background: var(--tg-theme-bg-color);
}

.header {
  padding: 16px;
  background: var(--tg-theme-bg-color);
  position: sticky;
  top: 0;
  z-index: 10;
}

.navigation-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--tg-theme-button-color);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.header {
  padding: 16px;
  position: sticky;
  top: 0;
  background: var(--tg-theme-bg-color);
  z-index: 10;
  text-align: center;
}

/* Стили для аккуратного гибридного входа */
.auth-card {
  text-align: center;
  width: 100%;
  max-width: 320px;
  margin-top: 40px;
}

.logo {
  font-size: 60px;
  margin-bottom: 10px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

input {
  padding: 14px;
  border-radius: 10px;
  border: 1px solid var(--tg-theme-hint-color);
  background: var(--tg-theme-secondary-bg-color);
  color: var(--tg-theme-text-color);
  font-size: 16px;
}

.primary-btn {
  background-color: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  padding: 14px;
  border-radius: 10px;
  border: none;
  font-weight: bold;
  cursor: pointer;
}

.divider {
  margin: 20px 0;
  border-bottom: 1px solid var(--tg-theme-hint-color);
  line-height: 0.1em;
  opacity: 0.5;
}

.divider span {
  background: var(--tg-theme-bg-color);
  padding: 0 10px;
  font-size: 12px;
}

.bio-btn {
  background: none;
  border: 1px solid var(--tg-theme-button-color);
  color: var(--tg-theme-button-color);
  padding: 12px;
  border-radius: 10px;
  width: 100%;
  font-weight: 500;
}

.app-container {
  /* Используем переменную вьюпорта Telegram для мобилок */
  height: var(--tg-viewport-height, 100vh);
  display: flex;
  flex-direction: column;
  background: var(--tg-theme-bg-color);
}

.vault-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Скроллиться будут только внутренние компоненты */
}


.auth-wrapper, .vault-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 20px 16px 10px;
  background: var(--tg-theme-bg-color);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header h1 {
  font-size: 24px;
  margin: 0;
}

.main-menu {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
}

.menu-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  width: 100%;
  max-width: 500px; /* Чтобы на широких экранах кнопки не расползались слишком сильно */
}

.menu-item {
  background: var(--tg-theme-secondary-bg-color);
  border: none;
  border-radius: 16px;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.1s ease;
}

.menu-item:active {
  transform: scale(0.95);
}

.menu-icon {
  font-size: 32px;
}

.menu-label {
  color: var(--tg-theme-text-color);
  font-weight: 600;
  font-size: 14px;
  text-align: center;
}

.placeholder-screen {
  padding: 40px;
  text-align: center;
  color: var(--tg-theme-hint-color);
}
</style>