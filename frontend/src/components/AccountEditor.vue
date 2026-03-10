<script setup>
import {ref, onMounted} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {platformApi} from '../api/platform.js';
import {accountApi} from '../api/account.js';

const props = defineProps(['account', 'currentPlatform']);
const emit = defineEmits(['save']);
const {tg, initData} = useTelegram();

const platforms = ref([]);
const showPassword = ref(false);
const showConfirmDialog = ref(false);
const isSaving = ref(false);
const copyFeedback = ref('');
const editedData = ref({
  ...props.account,
  platform_id: props.currentPlatform?.id || props.account?.platform_id || '',
  email: props.account?.email || '',
  phone: props.account?.phone || '',
  login: props.account?.login || '',
  password: props.account?.password || '',
  label: props.account?.label || ''
});

onMounted(async () => {
  try {
    // Используем правильный API для платформ
    platforms.value = await platformApi.getList(initData);
  } catch (e) {
    console.error("Ошибка загрузки платформ:", e);
  }
});

const copyToClipboard = (text, fieldName) => {
  if (!text) return;
  if (tg && tg.openTelegramLink) {
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
      alert(`Скопируйте текст вручную:\n\n${text}`);
    }
  } else {
    try {
      navigator.clipboard.writeText(text).then(() => showCopyFeedback(fieldName));
    } catch (err) {
      alert(`Скопируйте текст вручную:\n\n${text}`);
    }
  }
};

const showCopyFeedback = (fieldName) => {
  tg.HapticFeedback.notificationOccurred('success');
  copyFeedback.value = fieldName;
  setTimeout(() => copyFeedback.value = '', 1500);
};

const handleSave = () => {
  if (!editedData.value.platform_id || !editedData.value.login || !editedData.value.password) {
    tg.showAlert("Заполните платформу, логин и пароль");
    return;
  }
  tg.HapticFeedback.impactOccurred('medium');
  showConfirmDialog.value = true;
};

const confirmSave = async () => {
  showConfirmDialog.value = false;
  isSaving.value = true;

  try {
    // Реальный вызов API для сохранения в базу
    if (props.account?.id) {
      await accountApi.update(initData, props.account.id, editedData.value);
    } else {
      await accountApi.create(initData, editedData.value);
    }
    tg.HapticFeedback.notificationOccurred('success');
    emit('save', editedData.value); // Возвращаемся назад
  } catch (error) {
    console.error("Ошибка сохранения аккаунта:", error);
    tg.showAlert("Ошибка при сохранении аккаунта");
  } finally {
    isSaving.value = false;
  }
};

const cancelSave = () => showConfirmDialog.value = false;
</script>

<template>
  <div class="editor-wrapper">
    <div class="editor-container">
      <div class="field">
        <label>Платформа</label>
        <div class="select-wrapper">
          <select v-model="editedData.platform_id" class="custom-select">
            <option disabled value="">Выберите платформу</option>
            <option v-for="p in platforms" :key="p.id" :value="p.id">
              {{ p.icon }} {{ p.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="field">
        <label>Username / Login</label>
        <div class="input-row">
          <input v-model="editedData.login" type="text" placeholder="Логин"/>
          <button class="action-btn" :class="{ feedback: copyFeedback === 'login' }"
                  @click="copyToClipboard(editedData.login, 'login')">
            {{ copyFeedback === 'login' ? '✓' : '📋' }}
          </button>
        </div>
      </div>

      <div class="field">
        <label>Password</label>
        <div class="input-row">
          <input v-model="editedData.password" :type="showPassword ? 'text' : 'password'" placeholder="Пароль"/>
          <button class="action-btn" @click="showPassword = !showPassword">{{ showPassword ? '🔓' : '🔒' }}</button>
          <button class="action-btn" :class="{ feedback: copyFeedback === 'password' }"
                  @click="copyToClipboard(editedData.password, 'password')">
            {{ copyFeedback === 'password' ? '✓' : '📋' }}
          </button>
        </div>
      </div>

      <div class="field">
        <label>Email</label>
        <div class="input-row">
          <input v-model="editedData.email" type="email" placeholder="Email"/>
          <button class="action-btn" :class="{ feedback: copyFeedback === 'email' }"
                  @click="copyToClipboard(editedData.email, 'email')">
            {{ copyFeedback === 'email' ? '✓' : '📋' }}
          </button>
        </div>
      </div>

      <div class="field">
        <label>Phone</label>
        <div class="input-row">
          <input v-model="editedData.phone" type="tel" placeholder="Phone number"/>
          <button class="action-btn" :class="{ feedback: copyFeedback === 'phone' }"
                  @click="copyToClipboard(editedData.phone, 'phone')">
            {{ copyFeedback === 'phone' ? '✓' : '📋' }}
          </button>
        </div>
      </div>

      <div class="field">
        <label>Tag</label>
        <input v-model="editedData.label" type="text" placeholder="Например: Личный" class="full-input"/>
      </div>

      <button class="save-btn" @click="handleSave" :disabled="isSaving">
        {{ isSaving ? 'Сохранение...' : 'Сохранить' }}
      </button>
    </div>

    <div v-if="showConfirmDialog" class="confirm-overlay" @click.self="cancelSave">
      <div class="confirm-dialog">
        <h2>Подтвердить сохранение?</h2>
        <p>Вы уверены, что хотите сохранить изменения?</p>
        <div class="confirm-buttons">
          <button class="btn-cancel" @click="cancelSave">Нет</button>
          <button class="btn-confirm" @click="confirmSave">Да</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Твои стили без изменений, добавляю только для полной сборки */
* {
  box-sizing: border-box;
}

.editor-wrapper {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  background: var(--tg-theme-bg-color);
  overflow: hidden;
  width: 100%;
  align-items: center;
  position: relative;
}

.editor-container {
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

.field {
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

.input-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

input, .custom-select {
  appearance: none;
  -webkit-appearance: none;
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(128, 128, 128, 0.3);
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: var(--tg-theme-text-color);
  font-size: 15px;
  outline: none;
  transition: all 0.2s ease;
}

input:focus, .custom-select:focus {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(128, 128, 128, 0.5);
}

input::placeholder {
  color: var(--tg-theme-hint-color);
}

.custom-select {
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23888' d='M2 4l4 4 4-4z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 30px;
}

.action-btn {
  flex: 0 0 44px;
  height: 44px;
  border-radius: 10px;
  border: none;
  background: var(--tg-theme-button-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
  transition: all 0.2s ease;
  font-size: 20px;
}

.action-btn:active {
  opacity: 0.7;
  transform: scale(0.95);
}

.action-btn.feedback {
  background: #4CAF50;
}

.save-btn {
  margin-top: 10px;
  padding: 14px;
  border-radius: 12px;
  border: none;
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.full-input {
  width: 100%;
}

.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}

.confirm-dialog {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 24px;
  max-width: 300px;
  width: 90%;
  text-align: center;
  animation: slideUp 0.3s ease;
}

.confirm-dialog h2 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: var(--tg-theme-text-color);
}

.confirm-dialog p {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: var(--tg-theme-hint-color);
}

.confirm-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
}

.btn-cancel, .btn-confirm {
  flex: 1;
  padding: 12px;
  border-radius: 10px;
  border: none;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: var(--tg-theme-hint-color);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-confirm {
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>