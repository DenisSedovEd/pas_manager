<script setup>
import { ref, onMounted } from 'vue';
import { useTelegram } from '../composables/useTelegram';
import { vaultApi } from '../api/vault';

const props = defineProps(['account', 'currentPlatform']);
const emit = defineEmits(['save']);
const { tg, initData } = useTelegram();

const platforms = ref([]);
const editedData = ref({
  ...props.account,
  platform_id: props.currentPlatform?.id || props.account?.platform_id
});

onMounted(async () => {
  try {
    platforms.value = await vaultApi.getPlatforms(initData);
  } catch (e) {
    console.error("Ошибка загрузки платформ:", e);
  }
});

const copyToClipboard = (text) => {
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    tg.HapticFeedback.notificationOccurred('success');
    tg.showAlert("Скопировано!");
  });
};

const handleSave = () => {
  tg.HapticFeedback.impactOccurred('medium');
  emit('save', editedData.value);
};
</script>

<template>
  <div class="editor-container">

    <div class="field">
      <label>Платформа</label>
      <div class="select-wrapper">
        <select v-model="editedData.platform_id" class="custom-select">
          <option v-for="p in platforms" :key="p.id" :value="p.id">
            {{ p.icon }} {{ p.name }}
          </option>
        </select>
      </div>
    </div>

    <div class="field">
      <label>Username / Login</label>
      <div class="input-row">
        <input v-model="editedData.login" type="text" placeholder="Логин" />
        <button class="action-btn" @click="copyToClipboard(editedData.login)">📋</button>
      </div>
    </div>

    <div class="field">
      <label>Password</label>
      <div class="input-row">
        <input v-model="editedData.password" type="text" placeholder="Пароль" />
        <button class="action-btn" @click="copyToClipboard(editedData.password)">📋</button>
      </div>
    </div>

    <div class="field">
      <label>Метка</label>
      <input v-model="editedData.label" type="text" placeholder="Например: Личный" class="full-input" />
    </div>

    <button class="save-btn" @click="handleSave">Сохранить</button>
  </div>
</template>

<style scoped>
/* Глобальный сброс для всех элементов внутри компонента */
* { box-sizing: border-box; }

.editor-container {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--tg-theme-bg-color);
  min-height: 100%;
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
  gap: 8px; /* Небольшой зазор между инпутом и кнопкой */
  width: 100%;
}

/* Стили для инпутов и селекта */
input, .custom-select {
  appearance: none; /* Убирает дефолтные стили браузера */
  -webkit-appearance: none;
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(128, 128, 128, 0.2);
  background: var(--tg-theme-secondary-bg-color) !important;
  color: var(--tg-theme-text-color);
  font-size: 15px;
  outline: none;
}

/* Специально для селекта, чтобы он не был белым */
.custom-select {
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23888' d='M2 4l4 4 4-4z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 30px;
}

.action-btn {
  flex: 0 0 44px; /* Фиксированная ширина, не сжимается */
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
}

.action-btn:active, .save-btn:active {
  opacity: 0.7;
}
</style>