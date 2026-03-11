<script setup>
import {ref, onMounted} from 'vue';
import {useTelegram} from './composables/useTelegram';
import {authApi} from './api/auth.js';
import PlatformList from './components/PlatformList.vue';
import AccountList from './components/AccountList.vue';
import AccountDetail from "./components/AccountDetail.vue";
import AccountEditor from "./components/AccountEditor.vue";
import PlatformEditor from "./components/PlatformEditor.vue";

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

  bio.init(async () => {
    isBioSupported.value = bio.isInited && bio.isBiometricAvailable;
    try {
      const status = await authApi.getStatus(initData);
      isUnlocked.value = status.is_unlocked;
      if (!isUnlocked.value && isBioSupported.value) {
        const bioSettings = await authApi.getBioSettings(initData);
        if (bioSettings.is_enabled) {
          authenticateWithBio(); // Автовызов окна FaceID
        }
      }
    } catch (e) {
      console.error("Ошибка проверки статуса:", e);
    }
  });

  window.addEventListener('beforeunload', () => {
    navigator.sendBeacon('/pas-manager/v1/main/auth/logout', initData);
  });
});

const handlePasswordUnlock = async () => {
  if (!password.value) return;
  isAuthLoading.value = true;
  try {
    const res = await authApi.unlockWithPassword(initData, password.value);
    if (res.ok) {
      isUnlocked.value = true;

      // Логика регистрации биометрии
      if (isBioSupported.value) {
        const bioSettings = await authApi.getBioSettings(initData);

        if (!bioSettings.is_enabled) {
          // Вызываем стандартное окно Telegram
          bio.authenticate({reason: 'Включить вход по FaceID'}, async (success, token) => {
            if (success) {
              try {
                // ОТПРАВЛЯЕМ ТОЛЬКО ТОКЕН.
                // Бэкенд сам возьмет пароль из сессии и зашифрует его этим токеном.
                await authApi.enableBiometric(initData, {bio_token: token});

                tg.showAlert("Биометрия успешно настроена!");
              } catch (e) {
                console.error("Ошибка сохранения биометрии:", e);
              }
            }
          });
        }
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
      // Отправляем токен на сервер, чтобы он нашел зашифрованный пароль
      const res = await authApi.unlockWithBiometric(initData, token);
      if (res.ok) {
        isUnlocked.value = true;
      } else {
        tg.showAlert("Ошибка биометрии. Введите пароль вручную.");
      }
    }
  });
};

const onAccountSelect = (account) => {
  editingAccount.value = account;
  currentScreen.value = 'account_view';
};

const onPlatformSelect = (platform) => {
  selectedPlatform.value = platform;
  currentScreen.value = 'accounts';
};

const onEditPlatform = (platform) => {
  selectedPlatform.value = platform;
  currentScreen.value = 'edit_platform';
};

const handleAccountSave = (updatedAccount) => {
  if (selectedPlatform.value && selectedPlatform.value.id !== updatedAccount.platform_id) {
    selectedPlatform.value = null;
    currentScreen.value = 'platforms';
  } else {
    currentScreen.value = 'accounts';
  }

  editingAccount.value = null;
  tg.HapticFeedback.notificationOccurred('success');
};

const goBack = () => {
  if (currentScreen.value === 'account_view' || currentScreen.value === 'account_edit') {
    currentScreen.value = 'accounts';
    editingAccount.value = null;
  } else if (currentScreen.value === 'accounts') {
    currentScreen.value = 'platforms';
    selectedPlatform.value = null;
  } else if (currentScreen.value === 'add_account') {
    currentScreen.value = 'accounts';
  } else if (currentScreen.value === 'add_platform') {
    currentScreen.value = 'platforms';
  } else if (currentScreen.value === 'edit_platform') {
    currentScreen.value = 'accounts';
  } else {
    currentScreen.value = 'menu';
  }
};

const openMyAccounts = () => currentScreen.value = 'platforms';
const openAddAccount = () => currentScreen.value = 'add_account';
const openAddPlatform = () => currentScreen.value = 'add_platform';

const onAccountDeleted = () => {
  currentScreen.value = 'accounts';
  editingAccount.value = null;
};

const onPlatformCreated = () => {
  currentScreen.value = 'platforms';
  selectedPlatform.value = null;
};

const onPlatformSaved = (result) => {
  if (result.deleted) {
    currentScreen.value = 'platforms';
    selectedPlatform.value = null;
  } else {
    currentScreen.value = 'accounts';
  }
};

const openEditAccount = (fullAccountData) => {
  if (fullAccountData) {
    editingAccount.value = fullAccountData;
  }
  currentScreen.value = 'account_edit';
};
</script>

<template>
  <div class="app-container">

    <div v-if="!isUnlocked" class="auth-card">
      <div class="logo">🛡️</div>
      <h1>Safe Manager</h1>
      <div class="input-group">
        <input v-model="password" type="password" placeholder="Мастер-пароль" @keyup.enter="handlePasswordUnlock"/>
        <button @click="handlePasswordUnlock" class="primary-btn" :disabled="isAuthLoading">
          {{ isAuthLoading ? 'Вход...' : 'Войти' }}
        </button>
      </div>
      <div v-if="isBioSupported" class="bio-section">
        <div class="divider"><span>или</span></div>
        <button @click="authenticateWithBio" class="bio-btn">🧬 Использовать FaceID</button>
      </div>
    </div>

    <div v-else class="vault-wrapper">
      <div v-if="currentScreen === 'menu'" class="main-menu">
        <div class="header"><h1>Safe Manager</h1></div>
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
            <div class="spacer"></div>
          </div>
        </div>
        <PlatformList @select-platform="onPlatformSelect" @add-platform="openAddPlatform"/>
      </div>

      <div v-else-if="currentScreen === 'accounts'">
        <div class="header">
          <div class="navigation-row center-elements">
            <button @click="goBack" class="back-btn">←</button>
            <div class="header-platform-info">
              <span class="header-icon">{{ selectedPlatform?.icon }}</span>
              <div class="title-with-desc">
                <h1>{{ selectedPlatform?.name }}</h1>
                <p v-if="selectedPlatform?.description" class="header-desc">
                  {{ selectedPlatform.description }}
                </p>
              </div>
            </div>
            <button
                v-if="selectedPlatform?.name !== 'Other'"
                class="header-edit-btn"
                @click="onEditPlatform(selectedPlatform)"
            >
              ✏️
            </button>
            <div v-else class="spacer"></div>
          </div>
        </div>
        <AccountList :platform-id="selectedPlatform?.id" @select-account="onAccountSelect"
                     @add-account="openAddAccount"/>
      </div>

      <div v-else-if="currentScreen === 'account_view'">
        <div class="header">
          <div class="navigation-row">
            <button @click="goBack" class="back-btn">←</button>
            <h1>Аккаунт</h1>
            <div class="spacer"></div>
          </div>
        </div>
        <AccountDetail :account="editingAccount" @edit="openEditAccount" @deleted="onAccountDeleted"/>
      </div>

      <div v-else-if="currentScreen === 'account_edit'">
        <div class="header">
          <div class="navigation-row">
            <button @click="goBack" class="back-btn">←</button>
            <h1>Редактировать</h1>
            <div class="spacer"></div>
          </div>
        </div>
        <AccountEditor :account="editingAccount" :currentPlatform="selectedPlatform" @save="handleAccountSave"/>
      </div>

      <div v-else-if="currentScreen === 'add_account'">
        <div class="header">
          <div class="navigation-row">
            <button @click="goBack" class="back-btn">←</button>
            <h1>Новый аккаунт</h1>
            <div class="spacer"></div>
          </div>
        </div>
        <AccountEditor @save="goBack" :currentPlatform="selectedPlatform"/>
      </div>

      <div v-else-if="currentScreen === 'add_platform'">
        <div class="header">
          <div class="navigation-row">
            <button @click="goBack" class="back-btn">←</button>
            <h1>Новая платформа</h1>
            <div class="spacer"></div>
          </div>
        </div>
        <PlatformEditor @save="onPlatformCreated"/>
      </div>

      <div v-else-if="currentScreen === 'edit_platform'">
        <div class="header">
          <div class="navigation-row">
            <button @click="goBack" class="back-btn">←</button>
            <h1>Редактировать платформу</h1>
            <div class="spacer"></div>
          </div>
        </div>
        <PlatformEditor :platform="selectedPlatform" @save="onPlatformSaved"/>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Твои базовые стили остаются */
:global(body) {
  margin: 0;
  padding: 0;
  background: var(--tg-theme-bg-color);
}

:global(html), :global(body) {
  margin: 0;
  padding: 0;
  background-color: var(--tg-theme-bg-color);
  color: var(--tg-theme-text-color);
  height: 100%;
  overflow: hidden;
}

.app-container {
  height: var(--tg-viewport-height, 100vh);
  display: flex;
  flex-direction: column;
  background: var(--tg-theme-bg-color);
}

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

/* Новые стили для шапки платформы */
.center-elements {
  justify-content: space-between;
}

.header-platform-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: center;
}

.header-icon {
  font-size: 20px;
}

.header-edit-btn {
  background: var(--tg-theme-button-color);
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.header-edit-btn:active {
  opacity: 0.7;
  transform: scale(0.95);
}

.back-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--tg-theme-button-color);
  cursor: pointer;
  padding: 0;
  line-height: 1;
  flex-shrink: 0;
  width: 24px;
  height: 24px;
}

.spacer {
  width: 32px;
  flex-shrink: 0;
}

.header h1 {
  font-size: 18px;
  margin: 0;
  text-align: center;
  line-height: 1.2;
}

/* Остальные стили для auth-card и main-menu без изменений */
.auth-card {
  text-align: center;
  width: 100%;
  max-width: 320px;
  margin-top: 40px;
  align-self: center;
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

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  cursor: pointer;
  transition: all 0.2s ease;
}

.bio-btn:active {
  opacity: 0.7;
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
  max-width: 500px;
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

.title-with-desc {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.header-desc {
  margin: 2px 0 0 0;
  font-size: 12px;
  color: var(--tg-theme-hint-color);
  font-weight: normal;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
  text-align: center;
}
</style>