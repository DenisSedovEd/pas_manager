<script setup>
import {ref, onMounted} from 'vue';
import {useRouter} from 'vue-router';
import {useTelegram} from '../composables/useTelegram';
import {authApi} from '../api/auth.js';

const router = useRouter();
const {tg, bio, initData} = useTelegram();

const password = ref('');
const isAuthLoading = ref(false);
const isBioSupported = ref(false);

onMounted(async () => {
  // 1. Инициализируем биометрию
  bio.init(async () => {
    isBioSupported.value = bio.isInited && bio.isBiometricAvailable;

    // 2. Проверяем статус (тот самый лог, который вы видите)
    try {
      const status = await authApi.getStatus(initData);
      if (status.is_unlocked) {
        router.push('/menu');
      }
    } catch (e) {
      console.error("Ошибка статуса:", e);
    }
  });
});

const handlePasswordUnlock = async () => {
  // Если пароль пуст или запрос уже идет — выходим
  if (!password.value || isAuthLoading.value) return;

  isAuthLoading.value = true;

  try {
    // ВЫЗОВ ЭНДПОИНТА UNLOCK
    const response = await authApi.unlock(initData, password.value);

    if (response.is_unlocked) {
      tg.HapticFeedback.notificationOccurred('success');
      router.push('/menu'); // Переход в меню
    } else {
      tg.showAlert("Доступ запрещен");
    }
  } catch (e) {
    console.error("Ошибка при разблокировке:", e);
    tg.HapticFeedback.notificationOccurred('error');
    tg.showAlert("Неверный пароль");
  } finally {
    isAuthLoading.value = false;
  }
};

const handleBioUnlock = async () => {
  bio.authenticate(async (isAuthenticated) => {
    if (isAuthenticated) {
      try {
        const response = await authApi.unlock(initData, 'biometric');
        if (response.is_unlocked) router.push('/menu');
      } catch (e) {
        tg.showAlert("Ошибка биометрии на сервере");
      }
    }
  });
};
</script>

<template>
  <div class="auth-page">
    <div class="icon">🛡️</div>
    <h2>Password Manager</h2>

    <div class="input-group">
      <input
          v-model="password"
          type="password"
          placeholder="Введите мастер-пароль"
          class="main-input"
          @keyup.enter="handlePasswordUnlock"
      />
      <button
          @click="handlePasswordUnlock"
          :disabled="isAuthLoading"
          class="login-btn"
      >
        {{ isAuthLoading ? 'Проверка...' : 'Войти' }}
      </button>
    </div>

    <div v-if="isBioSupported" class="bio-section">
      <div class="divider"><span>ИЛИ</span></div>
      <button @click="handleBioUnlock" class="bio-btn">
        Войти по отпечатку
      </button>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  gap: 20px;
}

.icon {
  font-size: 64px;
}

.input-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.main-input {
  padding: 14px;
  border-radius: 12px;
  border: 1px solid rgba(128, 128, 128, 0.3);
  background: var(--tg-theme-secondary-bg-color);
  color: var(--tg-theme-text-color);
  text-align: center;
  font-size: 16px;
}

.login-btn {
  padding: 16px;
  border-radius: 12px;
  border: none;
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  font-weight: bold;
}

.divider {
  width: 100%;
  text-align: center;
  border-bottom: 1px solid rgba(128, 128, 128, 0.2);
  line-height: 0.1em;
  margin: 10px 0;
}

.divider span {
  background: var(--tg-theme-bg-color);
  padding: 0 10px;
  color: gray;
  font-size: 12px;
}

.bio-btn {
  background: none;
  border: 1px solid var(--tg-theme-button-color);
  color: var(--tg-theme-button-color);
  padding: 12px;
  border-radius: 10px;
  width: 100%;
}
</style>