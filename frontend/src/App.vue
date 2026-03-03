<script setup>
import { ref, onMounted } from 'vue';
import { useTelegram } from './composables/useTelegram';
import { authApi } from './api/auth';

const { tg, bio, initApp, initData } = useTelegram();

const isUnlocked = ref(false);
const password = ref('');
const isBioSupported = ref(false);
const isAuthLoading = ref(false);

onMounted(async () => {
  initApp();

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
  bio.authenticate({ reason: 'Вход в сейф' }, async (success, token) => {
    if (success) {
      const res = await authApi.unlockWithBiometric(initData, token);
      if (res.ok) isUnlocked.value = true;
    }
  });
};
</script>

<template>
  <div class="container">
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
        <button @click="handlePasswordUnlock" class="primary-btn" :disabled="isAuthLoading">
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

    <div v-else class="vault-screen">
      <div class="status-badge">🔓 Сейф открыт</div>
      <div class="placeholder-content">
         <p>Ваши данные в безопасности.</p>
         <p style="font-size: 0.8em; color: var(--tg-theme-hint-color);">
           Чтобы закрыть сейф, просто закройте приложение.
         </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Добавим немного стиля для открытого состояния */
.status-badge {
  background: #4caf5022;
  color: #4caf50;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  display: inline-block;
}
.placeholder-content {
  text-align: center;
  margin-top: 40px;
}
/* Стили для аккуратного гибридного входа */
.auth-card {
  text-align: center;
  width: 100%;
  max-width: 320px;
  margin-top: 40px;
}
.logo { font-size: 60px; margin-bottom: 10px; }
.input-group { display: flex; flex-direction: column; gap: 12px; }

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
.divider span { background: var(--tg-theme-bg-color); padding: 0 10px; font-size: 12px; }

.bio-btn {
  background: none;
  border: 1px solid var(--tg-theme-button-color);
  color: var(--tg-theme-button-color);
  padding: 12px;
  border-radius: 10px;
  width: 100%;
  font-weight: 500;
}
</style>