<script setup>
import {ref, onMounted, onUnmounted} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {categoryApi} from '../api/category.js';
import {iconDisplayLabel} from '../api/customIcon.js';
import CategoryIcon from './CategoryIcon.vue';
import EmojiPicker from 'vue3-emoji-picker';
import 'vue3-emoji-picker/css';

const props = defineProps(['category', 'parentCategoryId']);
const emit = defineEmits(['save', 'cancel']);
const {tg, initData} = useTelegram();

const showPicker = ref(false);
const isLoading = ref(false);
const rootCategories = ref([]);

const formData = ref({
  id: props.category?.id || null,
  name: props.category?.name || '',
  icon: props.category?.icon || '🌐',
  description: props.category?.description || '',
  parent_id: props.category?.parent_id ?? props.parentCategoryId ?? null,
});

const isEditing = !!props.category?.id;

const onSelectEmoji = (emoji) => {
  formData.value.icon = emoji.i;
  showPicker.value = false;
};

const handleSave = async () => {
  if (!formData.value.name.trim()) {
    tg.showAlert("Введите название категории");
    return;
  }
  isLoading.value = true;
  tg.MainButton.showProgress(false);
  tg.MainButton.disable();
  try {
    if (isEditing) {
      await categoryApi.update(initData, formData.value.id, formData.value);
    } else {
      await categoryApi.create(initData, formData.value);
    }
    tg.HapticFeedback.notificationOccurred('success');
    emit('save');
  } catch (e) {
    tg.showAlert("Ошибка при сохранении");
  } finally {
    isLoading.value = false;
    tg.MainButton.hideProgress();
    tg.MainButton.enable();
  }
};

onMounted(async () => {
  tg.MainButton.setText(isEditing ? 'Обновить данные' : 'Создать категорию');
  tg.MainButton.onClick(handleSave);
  tg.MainButton.show();

  try {
    rootCategories.value = await categoryApi.getList(initData);
    if (isEditing && formData.value.id) {
      rootCategories.value = rootCategories.value.filter(c => c.id !== formData.value.id);
    }
  } catch (e) {
    // игнорируем — родитель необязателен
  }
});

onUnmounted(() => {
  tg.MainButton.hide();
  tg.MainButton.offClick(handleSave);
});
</script>

<template>
  <div class="editor-container">
    <div class="form">
      <div class="icon-section">
        <div class="icon-wrapper" @click="showPicker = !showPicker">
          <div class="icon-preview">
            <CategoryIcon :icon="formData.icon" fallback="🌐" size="xl" />
          </div>
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
        <label>Название категории</label>
        <input
            v-model="formData.name"
            type="text"
            placeholder="Например: ВКонтакте"
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

      <div class="input-group">
        <label>Родительская категория <span class="hint-inline">(необязательно)</span></label>
        <select v-model="formData.parent_id" class="main-input select-input">
          <option :value="null">— Корневая категория —</option>
          <option
              v-for="cat in rootCategories"
              :key="cat.id"
              :value="cat.id"
          >
            {{ iconDisplayLabel(cat.icon, '🌐') }} {{ cat.name }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<style scoped>
.editor-container {
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

.hint-inline {
  font-size: 11px;
  color: var(--tg-theme-hint-color);
  font-weight: normal;
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

.select-input {
  appearance: none;
  cursor: pointer;
}
</style>
