<script setup>
import {ref} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {resourceApi} from '../api/resource.js';

const emit = defineEmits(['save', 'cancel']);
const {tg, initData} = useTelegram();

const isLoading = ref(false);
const formData = ref({
  resource_name: '',
  description: ''
});

const handleSave = async () => {
  if (!formData.value.resource_name.trim()) {
    tg.showAlert('Введите название площадки');
    return;
  }
  isLoading.value = true;
  try {
    const created = await resourceApi.create(initData, formData.value);
    tg.HapticFeedback.notificationOccurred('success');
    emit('save', created);
  } catch (e) {
    tg.showAlert('Ошибка при сохранении');
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <!-- Затемнение фона -->
  <div class="modal-backdrop" @click.self="emit('cancel')">
    <div class="modal-card">

      <div class="modal-header">
        <span class="modal-title">Новая площадка</span>
        <button class="close-btn" @click="emit('cancel')">✕</button>
      </div>

      <div class="modal-body">
        <div class="input-group">
          <label>Название площадки</label>
          <input
              v-model="formData.resource_name"
              type="text"
              placeholder="Например: ВКонтакте"
              class="main-input"
              autofocus
          />
        </div>

        <div class="input-group">
          <label>Описание <span class="optional">(необязательно)</span></label>
          <input
              v-model="formData.description"
              type="text"
              placeholder="Краткое описание"
              class="main-input"
          />
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="emit('cancel')" :disabled="isLoading">
          Отмена
        </button>
        <button class="btn-save" @click="handleSave" :disabled="isLoading">
          <span v-if="isLoading">...</span>
          <span v-else>Добавить</span>
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: var(--tg-theme-bg-color);
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-width: 500px;
  padding: 8px 16px 32px;
  box-sizing: border-box;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 4px 16px;
}

.modal-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--tg-theme-text-color);
}

.close-btn {
  background: var(--tg-theme-secondary-bg-color);
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  font-size: 14px;
  color: var(--tg-theme-hint-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-size: 13px;
  color: var(--tg-theme-hint-color);
  margin-bottom: 8px;
  padding-left: 4px;
}

.optional {
  font-size: 11px;
  opacity: 0.6;
}

.main-input {
  width: 100%;
  background: var(--tg-theme-secondary-bg-color);
  border: 1px solid rgba(128, 128, 128, 0.2);
  border-radius: 12px;
  padding: 13px 16px;
  color: var(--tg-theme-text-color);
  font-size: 16px;
  box-sizing: border-box;
  outline: none;
}

.main-input:focus {
  border-color: var(--tg-theme-button-color);
}

.modal-footer {
  display: flex;
  gap: 10px;
}

.btn-cancel {
  flex: 1;
  padding: 13px;
  border-radius: 12px;
  border: 1px solid rgba(128, 128, 128, 0.25);
  background: var(--tg-theme-secondary-bg-color);
  color: var(--tg-theme-text-color);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
}

.btn-save {
  flex: 2;
  padding: 13px;
  border-radius: 12px;
  border: none;
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

.btn-save:disabled,
.btn-cancel:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>