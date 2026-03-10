<script setup>
import {ref, onMounted} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {platformApi} from '../api/platform.js';
import {accountApi} from '../api/account.js';

const props = defineProps(['account', 'currentPlatform']);
const emit = defineEmits(['save', 'cancel', 'deleted']);
const {tg, initData} = useTelegram();

const platforms = ref([]);
const showPassword = ref(false);
const showConfirmDialog = ref(false);
const isSaving = ref(false);

const editedData = ref({
  id: props.account?.id || null,
  label: props.account?.label || '',
  login: props.account?.login || '',
  password: props.account?.password || '',
  email: props.account?.email || '',
  phone: props.account?.phone || '',
  platform_id: props.currentPlatform?.id || props.account?.platform_id || ''
});

onMounted(async () => {
  try {
    const response = await platformApi.getList(initData);
    platforms.value = response.data || response;
  } catch (e) {
    console.error("Ошибка загрузки платформ:", e);
    tg.showAlert("Не удалось загрузить список платформ");
  }
});

const validateAndConfirm = () => {
  if (!editedData.value.login || !editedData.value.password || !editedData.value.platform_id) {
    tg.showAlert("Заполните логин, пароль и выберите платформу");
    return;
  }
  tg.HapticFeedback.impactOccurred('medium');
  showConfirmDialog.value = true;
};

const handleSave = async () => {
  showConfirmDialog.value = false;
  isSaving.value = true;
  try {
    let result;
    if (editedData.value.id) {
      result = await accountApi.update(initData, editedData.value.id, editedData.value);
    } else {
      result = await accountApi.create(initData, editedData.value);
    }
    tg.HapticFeedback.notificationOccurred('success');
    emit('save', result);
  } catch (error) {
    console.error('Ошибка сохранения:', error);
    tg.showAlert("Не удалось сохранить данные");
  } finally {
    isSaving.value = false;
  }
};

const handleDelete = () => {
  tg.showConfirm("Удалить этот аккаунт безвозвратно?", async (ok) => {
    if (ok) {
      try {
        await accountApi.delete(initData, editedData.value.id);
        tg.HapticFeedback.notificationOccurred('warning');
        emit('deleted');
      } catch (error) {
        console.error('Ошибка удаления:', error);
        tg.showAlert("Не удалось удалить аккаунт");
      }
    }
  });
};
</script>

<template>
  <div class="editor-wrapper">
    <div class="editor-container">
      <div class="header-row">
        <h2>{{ editedData.id ? 'Редактирование' : 'Новый аккаунт' }}</h2>
      </div>

      <div class="field-group">
        <label>Платформа *</label>
        <div class="field-row">
          <select v-model="editedData.platform_id" class="field-input select-input">
            <option disabled value="">Выберите сервис</option>
            <option v-for="p in platforms" :key="p.id" :value="p.id">
              {{ p.icon || '🌐' }} {{ p.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="field-group">
        <label>Username *</label>
        <div class="field-row">
          <input v-model="editedData.login" class="field-input" type="text" placeholder="Логин"/>
        </div>
      </div>

      <div class="field-group">
        <label>Password *</label>
        <div class="field-row">
          <input :type="showPassword ? 'text' : 'password'" v-model="editedData.password"
                 class="field-input password-text"/>
          <button class="view-btn" @click="showPassword = !showPassword">{{ showPassword ? '🙈' : '👁️' }}</button>
        </div>
      </div>

      <div class="field-group">
        <label>Email</label>
        <div class="field-row">
          <input v-model="editedData.email" class="field-input" type="email" placeholder="mail@example.com"/>
        </div>
      </div>

      <div class="field-group">
        <label>Phone</label>
        <div class="field-row">
          <input v-model="editedData.phone" class="field-input" type="tel" placeholder="+7..."/>
        </div>
      </div>

      <div class="field-group">
        <label>Название (опционально)</label>
        <div class="field-row">
          <input v-model="editedData.label" class="field-input" type="text" placeholder="Напр: Личный"/>
        </div>
      </div>

      <div class="button-group">
        <button class="save-btn" :disabled="isSaving" @click="validateAndConfirm">
          {{ isSaving ? 'Сохранение...' : '💾 Сохранить' }}
        </button>

        <button class="cancel-btn" @click="emit('cancel')">Отмена</button>

        <button v-if="editedData.id" class="delete-btn" @click="handleDelete">
          🗑️ Удалить аккаунт
        </button>
      </div>
    </div>

    <div v-if="showConfirmDialog" class="dialog-overlay" @click.self="showConfirmDialog = false">
      <div class="confirm-dialog">
        <h2>Сохранить?</h2>
        <div class="confirm-buttons">
          <button class="cancel-btn dialog-btn" @click="showConfirmDialog = false">Отмена</button>
          <button class="save-btn dialog-btn" @click="handleSave">Да</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.editor-wrapper {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  background: var(--tg-theme-bg-color);
  width: 100%;
  align-items: center;
}

.editor-container {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  overflow-y: auto;
  width: 92%;
  max-width: 500px;
  margin: 10px 0;
  max-height: calc(100% - 20px);
}

.header-row h2 {
  margin: 0;
  font-size: 18px;
  color: var(--tg-theme-text-color);
  text-align: center;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 12px;
  color: var(--tg-theme-hint-color);
  text-transform: uppercase;
  margin-left: 4px;
}

.field-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.field-input {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08); /* Фон инпутов */
  border: 1px solid rgba(128, 128, 128, 0.2);
  color: var(--tg-theme-text-color);
  font-size: 15px;
  outline: none;
}

.select-input {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 14px;
}

.password-text {
  font-family: monospace;
}

.view-btn {
  flex: 0 0 44px;
  height: 44px;
  border-radius: 12px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: var(--tg-theme-text-color);
  font-size: 18px;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

/* КНОПКА СОХРАНИТЬ */
.save-btn {
  padding: 14px;
  border-radius: 12px;
  border: none;
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  font-weight: 600;
  font-size: 16px;
}

/* КНОПКА ОТМЕНА (как инпуты) */
.cancel-btn {
  padding: 14px;
  border-radius: 12px;
  border: 1px solid rgba(128, 128, 128, 0.2);
  background: rgba(255, 255, 255, 0.08);
  color: var(--tg-theme-text-color);
  font-size: 15px;
}

/* КНОПКА УДАЛИТЬ (бледно-красная) */
.delete-btn {
  padding: 14px;
  border-radius: 12px;
  border: none;
  background: rgba(255, 79, 79, 0.15); /* Бледно-красный фон */
  color: #ff4f4f;
  font-weight: 600;
  font-size: 15px;
  margin-top: 4px;
}

.delete-btn:active {
  background: rgba(255, 79, 79, 0.25);
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.confirm-dialog {
  background: var(--tg-theme-bg-color);
  border-radius: 20px;
  padding: 24px;
  width: 80%;
  max-width: 300px;
  text-align: center;
}

.confirm-buttons {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.dialog-btn {
  flex: 1;
  padding: 12px;
  border-radius: 10px;
  border: none;
}
</style>