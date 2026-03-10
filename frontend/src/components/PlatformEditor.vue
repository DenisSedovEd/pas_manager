<script setup>
import { ref, onMounted } from 'vue';
import { useTelegram } from '../composables/useTelegram';
import { platformApi } from '../api/platform.js';

const emit = defineEmits(['save']);
const { tg, initData } = useTelegram();

const showConfirmDialog = ref(false);
const isLoading = ref(false);
const nameInput = ref(null);
const descriptionInput = ref(null);

const formData = ref({
  name: '',
  icon: '🌐',
  description: ''
});

onMounted(() => {
  // Убираем автокоррекцию и автокапитализацию
  if (nameInput.value) {
    nameInput.value.setAttribute('autocorrect', 'off');
    nameInput.value.setAttribute('autocapitalize', 'off');
  }
  if (descriptionInput.value) {
    descriptionInput.value.setAttribute('autocorrect', 'off');
    descriptionInput.value.setAttribute('autocapitalize', 'off');
  }
});

const handleNameInput = (e) => {
  // Позволяем любые символы, включая кириллицу
  formData.value.name = e.target.value;
};

const handleDescriptionInput = (e) => {
  formData.value.description = e.target.value;
};

const handleSave = () => {
  if (!formData.value.name.trim()) {
    tg.showAlert("Укажите название платформы");
    return;
  }

  tg.HapticFeedback.impactOccurred('medium');
  showConfirmDialog.value = true;
};

const confirmSave = async () => {
  showConfirmDialog.value = false;
  isLoading.value = true;

  try {
    const result = await platformApi.create(initData, {
      name: formData.value.name,
      icon: formData.value.icon,
      description: formData.value.description || undefined
    });

    tg.HapticFeedback.notificationOccurred('success');
    tg.showAlert("Платформа создана!");
    emit('save', result);
  } catch (error) {
    console.error('Ошибка при создании платформы:', error);
    tg.showAlert('Ошибка при создании платформы');
  } finally {
    isLoading.value = false;
  }
};

const cancelSave = () => {
  showConfirmDialog.value = false;
};

const commonIcons = [
  '🌐', '📱', '💻', '🔐', '💳', '📧',
  '🎮', '🏠', '⚙️', '🛡️', '🔑', '📊',
  '🎯', '🚀', '📚', '🎨', '🎭', '🎪',
  '🎬', '🎤', '🎧', '🎵', '🎸', '🎹',
  '📷', '📹', '📺', '📻', '📡', '📞',
  '📠', '📱', '💾', '💿', '📀', '🖥️',
  '🖨️', '⌨️', '🖱️', '🖲️', '🕹️', '🗜️',
  '💽', '🔌', '🔋', '🔆', '🔅', '🌟',
  '⭐', '✨', '⚡', '🔥', '💥', '❄️',
  '🌈', '☀️', '🌤️', '⛅', '🌥️', '☁️'
];
</script>

<template>
  <div class="editor-wrapper">
    <div class="editor-container">

      <div class="field">
        <label>Название платформы</label>
        <input
          ref="nameInput"
          type="text"
          placeholder="Например: Gmail"
          maxlength="50"
          :value="formData.name"
          @input="handleNameInput"
          @compositionstart="true"
          @compositionend="true"
          inputmode="text"
        />
      </div>

      <div class="field">
        <label>Выберите иконку</label>
        <div class="icon-selector">
          <button
            v-for="icon in commonIcons"
            :key="icon"
            class="icon-button"
            :class="{ active: formData.icon === icon }"
            @click="formData.icon = icon"
          >
            {{ icon }}
          </button>
        </div>
      </div>

      <div class="field">
        <label>Текущая иконка</label>
        <div class="current-icon">{{ formData.icon }}</div>
      </div>

      <div class="field">
        <label>Описание (опционально)</label>
        <input
          ref="descriptionInput"
          type="text"
          placeholder="Добавьте описание"
          maxlength="100"
          :value="formData.description"
          @input="handleDescriptionInput"
          @compositionstart="true"
          @compositionend="true"
          inputmode="text"
        />
      </div>

      <button class="save-btn" @click="handleSave" :disabled="isLoading">
        {{ isLoading ? 'Создание...' : 'Создать платформу' }}
      </button>
    </div>

    <!-- Диалог подтверждения -->
    <div v-if="showConfirmDialog" class="confirm-overlay" @click.self="cancelSave">
      <div class="confirm-dialog">
        <h2>Создать платформу?</h2>
        <p>{{ formData.icon }} {{ formData.name }}</p>
        <p v-if="formData.description" class="description">{{ formData.description }}</p>
        <div class="confirm-buttons">
          <button class="btn-cancel" @click="cancelSave">Нет</button>
          <button class="btn-confirm" @click="confirmSave">Да</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
* { box-sizing: border-box; }

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

.editor-container::-webkit-scrollbar {
  width: 6px;
}

.editor-container::-webkit-scrollbar-track {
  background: transparent;
}

.editor-container::-webkit-scrollbar-thumb {
  background: rgba(128, 128, 128, 0.5);
  border-radius: 3px;
}

.editor-container::-webkit-scrollbar-thumb:hover {
  background: rgba(128, 128, 128, 0.7);
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

input {
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
  font-family: inherit;
  -webkit-user-select: text;
  user-select: text;
}

input:focus {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(128, 128, 128, 0.5);
}

input::placeholder {
  color: var(--tg-theme-hint-color);
}

.icon-selector {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 4px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  max-height: 220px;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  scrollbar-color: rgba(128, 128, 128, 0.5) transparent;
}

.icon-selector::-webkit-scrollbar {
  width: 4px;
}

.icon-selector::-webkit-scrollbar-track {
  background: transparent;
}

.icon-selector::-webkit-scrollbar-thumb {
  background: rgba(128, 128, 128, 0.5);
  border-radius: 2px;
}

.icon-selector::-webkit-scrollbar-thumb:hover {
  background: rgba(128, 128, 128, 0.7);
}

.icon-button {
  aspect-ratio: 1;
  border: 2px solid rgba(128, 128, 128, 0.3);
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 8px;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  min-width: 0;
}

.icon-button:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(128, 128, 128, 0.5);
}

.icon-button.active {
  background: var(--tg-theme-button-color);
  border-color: var(--tg-theme-button-color);
  box-shadow: 0 0 8px rgba(88, 166, 255, 0.5);
}

.icon-button:active {
  transform: scale(0.92);
}

.current-icon {
  width: 100%;
  padding: 16px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(128, 128, 128, 0.3);
  font-size: 40px;
  text-align: center;
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

.save-btn:active:not(:disabled) {
  opacity: 0.7;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.confirm-dialog {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 24px;
  max-width: 300px;
  width: 90%;
  text-align: center;
  animation: slideUp 0.3s ease;
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

.confirm-dialog h2 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: var(--tg-theme-text-color);
}

.confirm-dialog p {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: var(--tg-theme-text-color);
}

.confirm-dialog .description {
  font-size: 12px;
  color: var(--tg-theme-hint-color);
  margin-bottom: 20px;
}

.confirm-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
  margin-top: 20px;
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

.btn-cancel:active {
  opacity: 0.7;
  transform: scale(0.98);
}

.btn-confirm {
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
}

.btn-confirm:active {
  opacity: 0.85;
  transform: scale(0.98);
}
</style>