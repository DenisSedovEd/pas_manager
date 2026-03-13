<script setup>
import {ref, computed, onMounted} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {accountApi} from '../api/account.js';
import {platformApi} from '../api/platform.js';

const props = defineProps(['account', 'currentPlatform']);
const emit = defineEmits(['save', 'cancel']);
const {tg, initData} = useTelegram();

const showConfirmDialog = ref(false);
const showSaveConfirmDialog = ref(false);
const isLoading = ref(false);
const showPassword = ref(false);
const platforms = ref([]);

onMounted(async () => {
  try {
    const response = await platformApi.getList(initData);
    platforms.value = response.data || response;
  } catch (e) {
    console.error("Ошибка загрузки платформ", e);
  }
});

const isEditing = computed(() => !!props.account?.id);

const selectedPlatform = computed(() => {
  return platforms.value.find(p => p.id === formData.value.platform_id) || props.currentPlatform;
});

const formData = ref({
  id: props.account?.id || null,
  platform_id: props.currentPlatform?.id || props.account?.platform_id,
  label: props.account?.label || '',
  login: props.account?.login || '',
  password: props.account?.password || '',
  email: props.account?.email || '',
  phone: props.account?.phone || ''
});

const handleSave = async () => {
  if (!formData.value.login.trim() || !formData.value.password.trim()) {
    tg.showAlert("Логин и пароль обязательны");
    return;
  }

  if (isEditing.value) {
    showSaveConfirmDialog.value = true;
  } else {
    executeSave();
  }
};

const executeSave = async () => {
  showSaveConfirmDialog.value = false;
  isLoading.value = true;
  try {
    if (isEditing.value) {
      await accountApi.update(initData, formData.value.id, formData.value);
    } else {
      await accountApi.create(initData, formData.value);
    }
    tg.HapticFeedback.notificationOccurred('success');
    emit('save');
  } catch (e) {
    tg.showAlert("Ошибка при сохранении");
  } finally {
    isLoading.value = false;
  }
};

const handleDelete = async () => {
  try {
    await accountApi.delete(initData, formData.value.id);
    tg.HapticFeedback.notificationOccurred('success');
    emit('save');
  } catch (e) {
    tg.showAlert("Ошибка при удалении");
  }
};

const generatePassword = () => {
  const charset = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*";
  const length = 16;

  const array = new Uint32Array(length);
  window.crypto.getRandomValues(array);

  let pass = "";
  for (let i = 0; i < length; i++) {
    pass += charset[array[i] % charset.length];
  }

  formData.value.password = pass;
  showPassword.value = true;

  tg.HapticFeedback.impactOccurred('medium');
};

</script>

<template>
  <div class="editor-container">
    <div class="form">

      <div class="icon-section">
        <div class="icon-preview">👤</div>
        <p class="platform-name">{{ currentPlatform?.name || 'Аккаунт' }}</p>
      </div>

      <div class="input-group">
        <label>Платформа</label>
        <select v-model="formData.platform_id" class="main-input select-input">
          <option v-for="p in platforms" :key="p.id" :value="p.id">
            {{ p.icon }} {{ p.name }}
          </option>
        </select>
      </div>

      <div class="input-group">
        <label>Название / Метка</label>
        <input
            v-model="formData.label"
            type="text"
            placeholder="Например: Основной"
            class="main-input"
        />
      </div>

      <div class="input-group">
        <label>Логин / Имя пользователя</label>
        <input
            v-model="formData.login"
            type="text"
            placeholder="username"
            class="main-input"
        />
      </div>

      <div class="input-group">
        <div class="label-row">
          <label>Пароль</label>
          <span class="generate-btn" @click="generatePassword">Сгенерировать</span>
        </div>
        <div class="password-wrapper">
          <input
              :type="showPassword ? 'text' : 'password'"
              v-model="formData.password"
              placeholder="••••••••"
              class="main-input"
          />
          <button
              class="eye-btn"
              @click.prevent="showPassword = !showPassword"
              type="button"
          >
            {{ showPassword ? '🔓' : '🔒' }}
          </button>
        </div>
      </div>

      <div class="input-group">
        <label>E-mail</label>
        <input
            v-model="formData.email"
            type="email"
            placeholder="example@mail.com"
            class="main-input"
        />
      </div>

      <div class="input-group">
        <label>Телефон</label>
        <input
            v-model="formData.phone"
            type="tel"
            placeholder="+7 (___) ___-__-__"
            class="main-input"
        />
      </div>

      <div class="actions">
        <button class="btn primary" @click="handleSave" :disabled="isLoading">
          {{ isLoading ? 'Сохранение...' : (isEditing ? 'Обновить данные' : 'Сохранить аккаунт') }}
        </button>

        <button v-if="isEditing" class="btn danger" @click="showConfirmDialog = true">
          Удалить аккаунт
        </button>
      </div>
    </div>

    <div v-if="showConfirmDialog" class="modal-overlay">
      <div class="modal">
        <h3>Удалить аккаунт?</h3>
        <p>Вы потеряете доступ к сохраненным данным этой учетной записи.</p>
        <div class="modal-buttons">
          <button class="btn danger" @click="handleDelete">Да, удалить</button>
          <button class="btn secondary" @click="showConfirmDialog = false">Отмена</button>
        </div>
      </div>
    </div>

    <div v-if="showSaveConfirmDialog" class="modal-overlay">
      <div class="modal">
        <h3>Сохранить изменения?</h3>
        <p>Текущие данные аккаунта будут обновлены.</p>
        <div class="modal-buttons">
          <button class="btn primary" @click="executeSave">Сохранить</button>
          <button class="btn secondary" @click="showSaveConfirmDialog = false">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.editor-container {
  padding: 16px;
  padding-bottom: 80px;
  max-width: 500px;
  margin: 0 auto;
}

.icon-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}

.icon-preview {
  font-size: 44px;
  width: 80px;
  height: 80px;
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(128, 128, 128, 0.1);
}

.platform-name {
  margin-top: 12px;
  font-weight: 600;
  font-size: 16px;
  color: var(--tg-theme-text-color);
}

.input-group {
  margin-bottom: 18px;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 6px;
  padding: 0 4px;
}

.input-group label {
  font-size: 13px;
  color: var(--tg-theme-hint-color);
}

.generate-btn {
  font-size: 12px;
  font-weight: 600;
  color: var(--tg-theme-button-color);
  cursor: pointer;
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.main-input {
  width: 100%;
  background: var(--tg-theme-secondary-bg-color);
  border: 1px solid rgba(128, 128, 128, 0.2);
  border-radius: 12px;
  padding: 12px 50px 12px 16px;
  color: var(--tg-theme-text-color);
  font-size: 16px;
  box-sizing: border-box;
  outline: none;
}

.main-input:focus {
  border-color: var(--tg-theme-button-color);
}

.eye-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  font-size: 20px;
  color: var(--tg-theme-text-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  pointer-events: auto;
}

.eye-btn:active {
  transform: translateY(-50%) scale(0.95);
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 30px;
}

.btn {
  padding: 14px;
  border-radius: 12px;
  border: none;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
}

.primary {
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
}

.secondary {
  background: transparent;
  color: var(--tg-theme-hint-color);
  border: 1px solid rgba(128, 128, 128, 0.2);
}

.danger {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: var(--tg-theme-bg-color);
  border-radius: 20px;
  padding: 24px;
  width: 85%;
  max-width: 320px;
  text-align: center;
}

.modal h3 {
  margin-bottom: 8px;
}

.modal p {
  color: var(--tg-theme-hint-color);
  font-size: 14px;
  margin-bottom: 24px;
}

.modal-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.select-input {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='rgba(128, 128, 128, 0.5)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 40px !important;
  cursor: pointer;
}
</style>