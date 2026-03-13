<script setup>
import {ref, onMounted} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {accountApi} from '../api/account.js';

const props = defineProps(['account']);
const emit = defineEmits(['edit', 'deleted']);
const {tg, initData} = useTelegram();

const fullAccount = ref(null);
const isLoading = ref(true);
const showPassword = ref(false);
const copyStatus = ref({}); // Для индикации копирования отдельных полей

onMounted(async () => {
  try {
    // Получаем детальные данные (с расшифрованным паролем и т.д.)
    fullAccount.value = await accountApi.getDetail(initData, props.account.id);
  } catch (error) {
    tg.showAlert("Не удалось загрузить данные");
  } finally {
    isLoading.value = false;
  }
});

const copyToClipboard = (text, field) => {
  if (!text) return;

  // Используем API Telegram или стандартный метод
  const el = document.createElement('textarea');
  el.value = text;
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);

  // Визуальный отклик
  tg.HapticFeedback.notificationOccurred('success');
  copyStatus.value[field] = true;
  setTimeout(() => {
    copyStatus.value[field] = false;
  }, 2000);
};
</script>

<template>
  <div class="detail-container">
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <template v-else-if="fullAccount">
      <div class="header-section">
        <div class="account-avatar">👤</div>
        <h2 class="account-title">{{ fullAccount.label || fullAccount.login }}</h2>
        <p class="account-subtitle">Детали аккаунта</p>
      </div>

      <div class="info-cards">

        <div class="info-card" @click="copyToClipboard(fullAccount.login, 'login')">
          <div class="card-content">
            <label>Логин</label>
            <div class="value">{{ fullAccount.login }}</div>
          </div>
          <div class="copy-icon" :class="{ 'copied': copyStatus['login'] }">
            {{ copyStatus['login'] ? '✅' : '📋' }}
          </div>
        </div>

        <div class="info-card password-card">
          <div class="card-content" @click="copyToClipboard(fullAccount.password, 'pass')">
            <label>Пароль</label>
            <div class="value">
              {{ showPassword ? fullAccount.password : '••••••••••••' }}
            </div>
          </div>
          <div class="card-actions">
            <button class="toggle-btn" @click="showPassword = !showPassword">
              {{ showPassword ? '🔓' : '🔒' }}
            </button>
            <div class="copy-icon" @click="copyToClipboard(fullAccount.password, 'pass')"
                 :class="{ 'copied': copyStatus['pass'] }">
              {{ copyStatus['pass'] ? '✅' : '📋' }}
            </div>
          </div>
        </div>

        <div v-if="fullAccount.email" class="info-card" @click="copyToClipboard(fullAccount.email, 'email')">
          <div class="card-content">
            <label>E-mail</label>
            <div class="value">{{ fullAccount.email }}</div>
          </div>
          <div class="copy-icon" :class="{ 'copied': copyStatus['email'] }">
            {{ copyStatus['email'] ? '✅' : '📋' }}
          </div>
        </div>

        <div v-if="fullAccount.phone" class="info-card" @click="copyToClipboard(fullAccount.phone, 'phone')">
          <div class="card-content">
            <label>Телефон</label>
            <div class="value">{{ fullAccount.phone }}</div>
          </div>
          <div class="copy-icon" :class="{ 'copied': copyStatus['phone'] }">
            {{ copyStatus['phone'] ? '✅' : '📋' }}
          </div>
        </div>

      </div>

      <div class="footer-actions">
        <button class="edit-btn" @click="emit('edit', fullAccount)">
          Изменить данные
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.detail-container {
  padding: 16px;
  padding-bottom: 40px;
}

.header-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}

.account-avatar {
  font-size: 44px;
  width: 80px;
  height: 80px;
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(128, 128, 128, 0.1);
  margin-bottom: 12px;
}

.account-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--tg-theme-text-color);
}

.account-subtitle {
  font-size: 13px;
  color: var(--tg-theme-hint-color);
  margin-top: 4px;
}

.info-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-card {
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 14px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: background 0.2s;
}

.info-card:active {
  background: rgba(128, 128, 128, 0.1);
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-content label {
  display: block;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--tg-theme-hint-color);
  margin-bottom: 4px;
}

.value {
  font-size: 16px;
  font-weight: 500;
  color: var(--tg-theme-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toggle-btn {
  background: none;
  border: none;
  font-size: 20px;
  padding: 0;
  cursor: pointer;
}

.copy-icon {
  font-size: 18px;
  opacity: 0.5;
  transition: all 0.2s;
}

.copy-icon.copied {
  opacity: 1;
  transform: scale(1.2);
}

.footer-actions {
  margin-top: 32px;
}

.edit-btn {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  border: none;
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 50px;
}
</style>