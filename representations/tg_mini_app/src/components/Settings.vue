<script setup>
import {ref, computed, onMounted, onUnmounted} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {resourceApi} from '../api/resource.js';
import {
  customIconApi,
  customIconFileUrl,
  isCustomIcon,
} from '../api/customIcon.js';
import CategoryIcon from './CategoryIcon.vue';
import EmojiPicker from 'vue3-emoji-picker';
import 'vue3-emoji-picker/css';

const props = defineProps({
  resources: {type: Array, default: () => []},
});
const emit = defineEmits(['resources-updated']);
const {tg, initData} = useTelegram();

const localResources = ref([]);
const editing = ref(null);
const isLoading = ref(false);
const showPicker = ref(false);
const pickerTab = ref('emoji');
const customIcons = ref([]);
const isUploading = ref(false);
const fileInput = ref(null);

const formData = ref({
  id: null,
  resource_name: '',
  description: '',
  icon: null,
});

const selectedCustomId = computed(() => {
  if (!isCustomIcon(formData.value.icon)) return null;
  return formData.value.icon.slice('custom:'.length);
});

const isDefaultResource = computed(
  () => editing.value?.resource_name === 'Без площадки'
);

const syncLocal = () => {
  localResources.value = [...props.resources].sort((a, b) =>
    (a.resource_name || '').localeCompare(b.resource_name || '', 'ru')
  );
};

const loadCustomIcons = async () => {
  customIcons.value = await customIconApi.getList(initData);
};

const openEdit = (resource) => {
  editing.value = resource;
  formData.value = {
    id: resource.id,
    resource_name: resource.resource_name || '',
    description: resource.description || '',
    icon: resource.icon || null,
  };
  showPicker.value = false;
  pickerTab.value = isCustomIcon(resource.icon) ? 'custom' : 'emoji';
  tg.MainButton.setText('Сохранить');
  tg.MainButton.show();
};

const cancelEdit = () => {
  editing.value = null;
  showPicker.value = false;
  tg.MainButton.hide();
};

const onSelectEmoji = (emoji) => {
  formData.value.icon = emoji.i;
  showPicker.value = false;
};

const onSelectCustom = (icon) => {
  formData.value.icon = icon.key;
  showPicker.value = false;
};

const clearIcon = () => {
  formData.value.icon = null;
  showPicker.value = false;
};

const openFilePicker = () => {
  fileInput.value?.click();
};

const onFileSelected = async (event) => {
  const file = event.target.files?.[0];
  event.target.value = '';
  if (!file) return;
  isUploading.value = true;
  try {
    const created = await customIconApi.upload(initData, file);
    customIcons.value = [created, ...customIcons.value];
    formData.value.icon = created.key;
    showPicker.value = false;
  } catch (err) {
    tg.showAlert(err.message || 'Ошибка загрузки иконки');
  } finally {
    isUploading.value = false;
  }
};

const deleteCustom = async (icon, event) => {
  event.stopPropagation();
  tg.showConfirm('Удалить эту иконку?', async (ok) => {
    if (!ok) return;
    try {
      await customIconApi.delete(initData, icon.id);
      customIcons.value = customIcons.value.filter((item) => item.id !== icon.id);
      if (formData.value.icon === icon.key) {
        formData.value.icon = null;
      }
      localResources.value = localResources.value.map((r) =>
        r.icon === icon.key ? {...r, icon: null} : r
      );
      emit('resources-updated', localResources.value);
    } catch {
      tg.showAlert('Ошибка удаления иконки');
    }
  });
};

const handleSave = async () => {
  if (!editing.value) return;
  if (!formData.value.resource_name.trim()) {
    tg.showAlert('Введите название площадки');
    return;
  }
  isLoading.value = true;
  tg.MainButton.showProgress(false);
  tg.MainButton.disable();
  try {
    const updated = await resourceApi.update(initData, formData.value.id, {
      resource_name: formData.value.resource_name.trim(),
      description: formData.value.description || null,
      icon: formData.value.icon || null,
    });
    localResources.value = localResources.value
      .map((r) => (r.id === updated.id ? updated : r))
      .sort((a, b) =>
        (a.resource_name || '').localeCompare(b.resource_name || '', 'ru')
      );
    emit('resources-updated', localResources.value);
    tg.HapticFeedback.notificationOccurred('success');
    cancelEdit();
  } catch (err) {
    tg.showAlert(err.message || 'Ошибка при сохранении');
  } finally {
    isLoading.value = false;
    tg.MainButton.hideProgress();
    tg.MainButton.enable();
  }
};

const handleDelete = () => {
  if (!editing.value || isDefaultResource.value) {
    tg.showAlert('Нельзя удалить системную площадку «Без площадки»');
    return;
  }
  const name = formData.value.resource_name;
  tg.showConfirm(
    `Удалить площадку «${name}»? Аккаунты будут перенесены на «Без площадки».`,
    async (ok) => {
      if (!ok) return;
      isLoading.value = true;
      try {
        await resourceApi.delete(initData, formData.value.id);
        localResources.value = localResources.value.filter(
          (r) => r.id !== formData.value.id
        );
        emit('resources-updated', localResources.value);
        tg.HapticFeedback.notificationOccurred('success');
        cancelEdit();
      } catch (err) {
        tg.showAlert(err.message || 'Ошибка при удалении');
      } finally {
        isLoading.value = false;
      }
    }
  );
};

onMounted(async () => {
  syncLocal();
  tg.MainButton.hide();
  tg.MainButton.onClick(handleSave);
  try {
    await loadCustomIcons();
  } catch {
    // галерея подтянется при открытии вкладки
  }
});

onUnmounted(() => {
  tg.MainButton.hide();
  tg.MainButton.offClick(handleSave);
});
</script>

<template>
  <div class="settings-container">
    <template v-if="!editing">
      <h2 class="title">Площадки</h2>
      <p class="section-hint">Переименование, иконка и удаление. При удалении аккаунты переносятся на «Без площадки».</p>
      <div v-if="!localResources.length" class="empty-state">Нет площадок</div>
      <div v-else class="list">
        <div
            v-for="resource in localResources"
            :key="resource.id"
            class="card-item"
            @click="openEdit(resource)"
        >
          <div class="icon-box">
            <CategoryIcon :icon="resource.icon" fallback="🌐" size="fill"/>
          </div>
          <div class="main-content">
            <div class="item-name">{{ resource.resource_name }}</div>
            <div v-if="resource.description" class="item-sub">{{ resource.description }}</div>
            <div v-else-if="!resource.icon" class="item-sub">Иконка категории</div>
          </div>
          <span class="chevron">›</span>
        </div>
      </div>
    </template>

    <div v-else class="form">
      <div class="icon-section">
        <div class="icon-wrapper" @click="showPicker = !showPicker">
          <div class="icon-preview">
            <CategoryIcon :icon="formData.icon" fallback="🌐" size="xl"/>
          </div>
          <div class="edit-badge">{{ showPicker ? '✕' : '⚙️' }}</div>
        </div>
        <p class="hint">
          {{ formData.icon ? 'Нажми, чтобы изменить' : 'Нет своей иконки — у аккаунтов будет иконка категории' }}
        </p>
        <button v-if="formData.icon" type="button" class="clear-icon-btn" @click="clearIcon">
          Сбросить (иконка категории)
        </button>
        <div v-if="showPicker" class="picker-container">
          <div class="picker-tabs">
            <button
                type="button"
                class="picker-tab"
                :class="{ active: pickerTab === 'emoji' }"
                @click="pickerTab = 'emoji'"
            >Эмодзи</button>
            <button
                type="button"
                class="picker-tab"
                :class="{ active: pickerTab === 'custom' }"
                @click="pickerTab = 'custom'"
            >Свои</button>
          </div>

          <EmojiPicker
              v-if="pickerTab === 'emoji'"
              :native="true"
              :theme="'dark'"
              :disable-skin-tones="true"
              @select="onSelectEmoji"
          />

          <div v-else class="custom-panel">
            <input
                ref="fileInput"
                type="file"
                accept="image/png,image/jpeg,image/webp,image/svg+xml"
                class="file-input"
                @change="onFileSelected"
            />
            <button
                type="button"
                class="upload-btn"
                :disabled="isUploading"
                @click="openFilePicker"
            >
              {{ isUploading ? 'Загрузка...' : '+ Загрузить иконку' }}
            </button>
            <p class="upload-hint">PNG, JPEG, WebP или SVG, до 512 KB</p>
            <div v-if="!customIcons.length" class="custom-empty">Пока нет своих иконок</div>
            <div v-else class="custom-grid">
              <button
                  v-for="icon in customIcons"
                  :key="icon.id"
                  type="button"
                  class="custom-item"
                  :class="{ selected: selectedCustomId === icon.id }"
                  @click="onSelectCustom(icon)"
              >
                <img :src="customIconFileUrl(icon.key)" alt="" class="custom-thumb"/>
                <span class="custom-delete" @click="deleteCustom(icon, $event)">✕</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="input-group">
        <label>Название</label>
        <input v-model="formData.resource_name" type="text" class="main-input" placeholder="Например: GitHub"/>
      </div>
      <div class="input-group">
        <label>Описание</label>
        <input v-model="formData.description" type="text" class="main-input" placeholder="Краткое описание"/>
      </div>
      <button type="button" class="cancel-btn" @click="cancelEdit">Отмена</button>
      <button
          v-if="!isDefaultResource"
          type="button"
          class="delete-btn"
          :disabled="isLoading"
          @click="handleDelete"
      >
        Удалить площадку
      </button>
    </div>
  </div>
</template>

<style scoped>
.settings-container {
  padding: 16px;
  width: 100%;
  box-sizing: border-box;
}

.title {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
}

.section-hint {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: var(--tg-theme-hint-color);
  line-height: 1.4;
}

.empty-state {
  text-align: center;
  color: var(--tg-theme-hint-color);
  padding: 2rem 0;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--tg-theme-secondary-bg-color, var(--tg-theme-bg-color));
  border-radius: 12px;
  cursor: pointer;
}

.icon-box {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-weight: 600;
}

.item-sub {
  font-size: 0.8rem;
  color: var(--tg-theme-hint-color);
  margin-top: 2px;
}

.chevron {
  color: var(--tg-theme-hint-color);
  font-size: 1.2rem;
}

.icon-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.icon-wrapper {
  position: relative;
  cursor: pointer;
}

.icon-preview {
  padding: 0.5rem;
  border-radius: 16px;
  background: var(--tg-theme-secondary-bg-color, rgba(255, 255, 255, 0.05));
  border: 2px dashed var(--tg-theme-hint-color);
  min-width: 4.5rem;
  min-height: 4.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-badge {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: var(--tg-theme-bg-color);
  border-radius: 50%;
  font-size: 0.9rem;
  padding: 2px;
}

.hint {
  font-size: 0.8rem;
  color: var(--tg-theme-hint-color);
  margin: 0;
  text-align: center;
  max-width: 280px;
}

.clear-icon-btn {
  border: none;
  background: transparent;
  color: var(--tg-theme-link-color, var(--tg-theme-button-color));
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0.25rem;
}

.picker-container {
  width: 100%;
  max-width: 352px;
  max-height: 360px;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.picker-tabs {
  display: flex;
  gap: 0.35rem;
  padding: 0.15rem;
  background: var(--tg-theme-secondary-bg-color, rgba(255, 255, 255, 0.05));
  border-radius: 10px;
}

.picker-tab {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--tg-theme-hint-color);
  padding: 0.45rem 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}

.picker-tab.active {
  background: var(--tg-theme-bg-color);
  color: var(--tg-theme-text-color);
}

.custom-panel {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.file-input { display: none; }

.upload-btn {
  border: 1px dashed var(--tg-theme-button-color);
  background: transparent;
  color: var(--tg-theme-button-color);
  border-radius: 10px;
  padding: 0.65rem;
  cursor: pointer;
}

.upload-btn:disabled { opacity: 0.6; }

.upload-hint,
.custom-empty {
  margin: 0;
  font-size: 0.75rem;
  color: var(--tg-theme-hint-color);
  text-align: center;
}

.custom-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.custom-item {
  position: relative;
  aspect-ratio: 1;
  border: 1px solid var(--tg-theme-hint-color);
  border-radius: 10px;
  background: var(--tg-theme-secondary-bg-color, rgba(255, 255, 255, 0.05));
  cursor: pointer;
  padding: 0.35rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-item.selected {
  border-color: var(--tg-theme-button-color);
}

.custom-thumb {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.custom-delete {
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 0.7rem;
  color: var(--tg-theme-hint-color);
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}

.input-group label {
  font-size: 0.85rem;
  color: var(--tg-theme-hint-color);
}

.main-input {
  padding: 12px;
  border-radius: 10px;
  border: 1px solid var(--tg-theme-hint-color);
  background: var(--tg-theme-bg-color);
  color: var(--tg-theme-text-color);
  font-size: 1rem;
}

.cancel-btn {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.7rem;
  border-radius: 10px;
  border: 1px solid var(--tg-theme-hint-color);
  background: transparent;
  color: var(--tg-theme-text-color);
  font-size: 0.95rem;
  cursor: pointer;
}

.delete-btn {
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.7rem;
  border-radius: 10px;
  border: 1px solid #e5484d;
  background: transparent;
  color: #e5484d;
  font-size: 0.95rem;
  cursor: pointer;
}

.delete-btn:disabled {
  opacity: 0.6;
  cursor: default;
}
</style>
