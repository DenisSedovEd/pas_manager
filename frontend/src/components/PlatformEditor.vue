<script setup>
import {ref} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {platformApi} from '../api/platform.js';
// Компоненты выбора эмодзи
import EmojiPicker from 'vue3-emoji-picker';
import 'vue3-emoji-picker/css';

const props = defineProps(['platform']);
const emit = defineEmits(['save', 'cancel']);
const {tg, initData} = useTelegram();

const showPicker = ref(false);
const isLoading = ref(false);

const formData = ref({
  id: props.platform?.id || null,
  name: props.platform?.name || '',
  icon: props.platform?.icon || '🌐',
  description: props.platform?.description || ''
});

const isEditing = !!props.platform?.id;

// Функция обновления иконки через пикер
const onSelectEmoji = (emoji) => {
  formData.value.icon = emoji.i;
  showPicker.value = false;
};

const handleSave = async () => {
  if (!formData.value.name.trim()) {
    tg.showAlert("Введите название платформы");
    return;
  }
  isLoading.value = true;
  try {
    if (isEditing) {
      await platformApi.update(initData, formData.value.id, formData.value);
    } else {
      await platformApi.create(initData, formData.value);
    }
    tg.HapticFeedback.notificationOccurred('success');
    emit('save');
  } catch (e) {
    tg.showAlert("Ошибка при сохранении");
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="editor-container">
    <div class="form">
      <div class="icon-section">
        <div class="icon-wrapper" @click="showPicker = !showPicker">
          <div class="icon-preview">{{ formData.icon }}</div>
          <div class="edit-badge">
            <span v-if="!showPicker">⚙️</span>
            <span v-else>✕</span>
          </div>
        </div>
        <p class="hint">Нажми на иконку, чтобы изменить</p>

        <div v-if="showPicker" class="picker-container">
          <EmojiPicker
              :native="true"
              :theme="'dark'"
              @select="onSelectEmoji"
              :disable-skin-tones="true"
              class="v3-emoji-picker"
          />
        </div>
      </div>

      <div class="input-group">
        <label>Название платформы</label>
        <input
            v-model="formData.name"
            type="text"
            placeholder="Например: Binance"
            class="main-input"
        />
      </div>

      <div class="input-group">
        <label>Описание</label>
        <textarea
            v-model="formData.description"
            placeholder="Для чего эта категория..."
            class="main-input"
            rows="3"
        ></textarea>
      </div>

      <div class="actions">
        <button class="btn primary" @click="handleSave" :disabled="isLoading">
          {{ isLoading ? 'Сохранение...' : (isEditing ? 'Обновить данные' : 'Создать платформу') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.editor-container {
  /* Убрали max-width и центрирование, теперь контейнер тянется на 100% */
  padding: 16px;
  width: 100%;
  box-sizing: border-box;
}

.form {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.icon-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
  position: relative;
}

.icon-wrapper {
  position: relative;
  cursor: pointer;
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
  border: 1px solid rgba(128, 128, 128, 0.2);
}

.edit-badge {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: var(--tg-theme-button-color);
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  border: 2px solid var(--tg-theme-bg-color);
}

.hint {
  font-size: 12px;
  color: var(--tg-theme-hint-color);
  margin-top: 8px;
}

.picker-container {
  position: absolute;
  top: 90px;
  z-index: 1000;
  width: 100%;
  display: flex;
  justify-content: center;
}

:deep(.v3-emoji-picker) {
  background: var(--tg-theme-secondary-bg-color) !important;
  border: 1px solid rgba(128, 128, 128, 0.2) !important;
  border-radius: 12px !important;
}

.input-group {
  margin-bottom: 20px;
  width: 100%;
}

.input-group label {
  display: block;
  font-size: 13px;
  color: var(--tg-theme-hint-color);
  margin-bottom: 8px;
  padding-left: 4px;
}

.main-input {
  /* Принудительно на всю ширину с учетом box-sizing */
  width: 100% !important;
  background: var(--tg-theme-secondary-bg-color);
  border: 1px solid rgba(128, 128, 128, 0.2);
  border-radius: 12px;
  padding: 14px 16px;
  color: var(--tg-theme-text-color);
  font-size: 16px;
  box-sizing: border-box;
  outline: none;
  display: block;
}

textarea.main-input {
  resize: none;
}

.actions {
  margin-top: 10px;
  width: 100%;
}

.btn {
  width: 100%; /* Кнопка на всю ширину */
  padding: 16px;
  border-radius: 12px;
  border: none;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn:active {
  opacity: 0.8;
}

.primary {
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
}
</style>