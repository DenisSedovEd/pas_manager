<script setup>
import { ref, onMounted } from 'vue';
import { useTelegram } from '../composables/useTelegram';
import { accountApi } from '../api/account.js';

const props = defineProps(['account']);
const emit = defineEmits(['edit', 'deleted']);
const { tg, initData } = useTelegram();

// Состояние для полных данных аккаунта и загрузки
const fullAccount = ref(null);
const isLoading = ref(true);
const copyFeedback = ref('');
const showPassword = ref(true); // По умолчанию пароль открыт, как ты просил

// Загружаем полные данные при открытии компонента
onMounted(async () => {
  isLoading.value = true;
  try {
    // Получаем расшифрованные данные с паролем, email и phone
    fullAccount.value = await accountApi.getDetail(initData, props.account.id);
  } catch (error) {
    console.error("Ошибка загрузки деталей:", error);
    tg.showAlert("Не удалось загрузить данные аккаунта");
  } finally {
    isLoading.value = false;
  }
});

const copyToClipboard = (text, fieldName) => {
  if (!text) return;

  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.left = '-999999px';
  document.body.appendChild(textarea);
  textarea.select();

  try {
    document.execCommand('copy');
    document.body.removeChild(textarea);
    showCopyFeedback(fieldName);
  } catch (err) {
    document.body.removeChild(textarea);
    tg.showAlert("Ошибка при копировании");
  }
};

const showCopyFeedback = (fieldName) => {
  tg.HapticFeedback.notificationOccurred('success');
  copyFeedback.value = fieldName;
  setTimeout(() => {
    copyFeedback.value = '';
  }, 1500);
};

const handleDelete = () => {
  tg.showConfirm("Удалить этот аккаунт?", async (ok) => {
    if (ok) {
      try {
        await accountApi.delete(initData, props.account.id);
        tg.HapticFeedback.notificationOccurred('success');
        emit('deleted');
      } catch (error) {
        console.error('Ошибка при удалении:', error);
        tg.showAlert('Ошибка при удалении аккаунта');
      }
    }
  });
};

const handleEdit = () => {
  // Передаем полные данные обратно, чтобы редактор знал пароль
  emit('edit', fullAccount.value || props.account);
};
</script>

<template>
  <div class="detail-wrapper">
    <div v-if="isLoading" class="loader-container">
      <div class="loader-text">Расшифровка данных...</div>
    </div>

    <div v-else class="detail-container">
      <div class="header-row">
        <h2>{{ fullAccount.label || props.account.label }}</h2>
        <button class="edit-btn" @click="handleEdit">✏️</button>
      </div>

      <div class="field-group">
        <label>Username</label>
        <div class="field-row">
          <div class="field-value">{{ fullAccount.login }}</div>
          <button
            class="copy-btn"
            :class="{ feedback: copyFeedback === 'login' }"
            @click="copyToClipboard(fullAccount.login, 'login')"
          >
            {{ copyFeedback === 'login' ? '✓' : '📋' }}
          </button>
        </div>
      </div>

      <div class="field-group">
        <label>Password</label>
        <div class="field-row">
          <div class="field-value password-text">
            {{ showPassword ? fullAccount.password : '••••••••' }}
          </div>
          <button class="view-btn" @click="showPassword = !showPassword">
            {{ showPassword ? '🙈' : '👁️' }}
          </button>
          <button
            class="copy-btn"
            :class="{ feedback: copyFeedback === 'password' }"
            @click="copyToClipboard(fullAccount.password, 'password')"
          >
            {{ copyFeedback === 'password' ? '✓' : '📋' }}
          </button>
        </div>
      </div>

      <div v-if="fullAccount.email" class="field-group">
        <label>Email</label>
        <div class="field-row">
          <div class="field-value">{{ fullAccount.email }}</div>
          <button
            class="copy-btn"
            :class="{ feedback: copyFeedback === 'email' }"
            @click="copyToClipboard(fullAccount.email, 'email')"
          >
            {{ copyFeedback === 'email' ? '✓' : '📋' }}
          </button>
        </div>
      </div>

      <div v-if="fullAccount.phone" class="field-group">
        <label>Phone</label>
        <div class="field-row">
          <div class="field-value">{{ fullAccount.phone }}</div>
          <button
            class="copy-btn"
            :class="{ feedback: copyFeedback === 'phone' }"
            @click="copyToClipboard(fullAccount.phone, 'phone')"
          >
            {{ copyFeedback === 'phone' ? '✓' : '📋' }}
          </button>
        </div>
      </div>

      <div class="button-group">
        <button class="delete-btn" @click="handleDelete">🗑️ Удалить аккаунт</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
* { box-sizing: border-box; }

.detail-wrapper {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  background: var(--tg-theme-bg-color);
  overflow: hidden;
  width: 100%;
  align-items: center;
  position: relative;
}

.loader-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.loader-text {
  color: var(--tg-theme-hint-color);
  font-size: 14px;
}

.detail-container {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  overflow-y: scroll;
  -webkit-overflow-scrolling: touch;
  width: 100%;
  max-width: 500px;
  margin: 16px;
  max-height: calc(100% - 32px);
  scrollbar-width: thin;
  scrollbar-color: rgba(128, 128, 128, 0.5) transparent;
}

.detail-container::-webkit-scrollbar { width: 6px; }
.detail-container::-webkit-scrollbar-track { background: transparent; }
.detail-container::-webkit-scrollbar-thumb { background: rgba(128, 128, 128, 0.5); border-radius: 3px; }

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

h2 {
  margin: 0;
  font-size: 20px;
  color: var(--tg-theme-text-color);
  flex: 1;
}

.edit-btn {
  flex-shrink: 0;
  background: var(--tg-theme-button-color);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 13px;
  color: var(--tg-theme-hint-color);
  font-weight: 500;
  margin-left: 4px;
}

.field-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.field-value {
  flex: 1;
  padding: 12px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(128, 128, 128, 0.3);
  color: var(--tg-theme-text-color);
  font-size: 14px;
  word-break: break-all;
  user-select: text;
  -webkit-user-select: text;
}

.password-text {
  font-family: monospace;
  font-size: 15px;
}

.copy-btn, .view-btn {
  flex: 0 0 44px;
  height: 44px;
  border-radius: 10px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  transition: all 0.2s ease;
  font-size: 18px;
}

.copy-btn {
  background: var(--tg-theme-button-color);
  color: white;
}

.view-btn {
  background: rgba(255, 255, 255, 0.1);
  color: var(--tg-theme-text-color);
}

.copy-btn:active, .view-btn:active {
  opacity: 0.7;
  transform: scale(0.95);
}

.copy-btn.feedback { background: #4CAF50; }

.button-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.delete-btn {
  padding: 12px;
  border-radius: 10px;
  border: 1px solid #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
}
</style>