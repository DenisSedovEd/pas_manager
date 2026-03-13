<script setup>
import {ref, onMounted} from 'vue';
import draggable from 'vuedraggable';
import {useTelegram} from '../composables/useTelegram';
import {platformApi} from '../api/platform.js';

const emit = defineEmits(['select-platform', 'add-platform']);
const {tg, initData} = useTelegram();
const platforms = ref([]);
const isLoading = ref(true);
const error = ref(null);
const isEditMode = ref(false);

const fetchPlatforms = async () => {
  try {
    const response = await platformApi.getList(initData);
    platforms.value = response.data || response;
  } catch (e) {
    tg.showAlert("Ошибка загрузки");
  }
};

const handleReorder = async () => {
  tg.HapticFeedback.impactOccurred('medium');
  try {
    const ids = platforms.value.map(p => String(p.id));
    await platformApi.reorder(initData, ids);
  } catch (e) {
    tg.showAlert("Ошибка сохранения порядка");
    await fetchPlatforms();
  }
};

const selectPlatform = (platform) => {
  if (isEditMode.value) return
  emit('select-platform', platform)
}

onMounted(async () => {
  try {
    await fetchPlatforms();
    const response = await platformApi.getList(initData);
    platforms.value = response.data || response;
  } catch (e) {
    console.error("Ошибка загрузки платформ:", e);
    error.value = "Не удалось загрузить данные";
  } finally {
    isLoading.value = false;
  }
});


</script>

<template>
  <div class="platforms-container">
    <div class="header-actions">
      <h2 class="title">Категории</h2>
      <button
          class="edit-mode-btn"
          @click="isEditMode = !isEditMode"
          @touchend.prevent="isEditMode = !isEditMode"
      >
        {{ isEditMode ? 'Готово' : 'Правка' }}
      </button>
    </div>

    <div v-if="isLoading" class="status-msg">
      <div class="spinner"></div>
      <p>Загрузка данных...</p>
    </div>

    <div v-else-if="error" class="status-msg error">
      <p>{{ error }}</p>
      <button @click="fetchPlatforms">Обновить</button>
    </div>

    <template v-else>
      <draggable
          v-model="platforms"
          item-key="id"
          class="platform-list"
          handle=".drag-handle"
          :disabled="!isEditMode"
          ghost-class="ghost-card"
          :force-fallback="true"
          fallback-class="sortable-fallback"
          @start="tg.HapticFeedback.impactOccurred('light')"
          @end="handleReorder"
      >
        <template #item="{ element: platform }">
          <div
              class="platform-item"
              :class="{ 'editing': isEditMode }"
              @click="!isEditMode && selectPlatform(platform)"
              @touchend.prevent="!isEditMode && selectPlatform(platform)"
              @contextmenu.prevent
          >
            <div class="icon-box">{{ platform.icon || '🌐' }}</div>
            <div class="main-content">
              <div class="name">{{ platform.name }}</div>
              <div v-if="platform.description" class="description">
                {{ platform.description }}
              </div>
            </div>

            <template v-if="!isEditMode">
              <div class="count-value">{{ platform.accounts_count || 0 }}</div>
              <div class="chevron">›</div>
            </template>

            <div v-if="isEditMode" class="drag-handle">☰</div>
          </div>
        </template>
      </draggable>

      <div v-if="!isEditMode" class="platform-item add-button" @click="emit('add-platform')">
        <div class="icon-box add-icon">+</div>
        <div class="main-content">
          <div class="name">Add New Platform</div>
          <div class="description">Create a new category</div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.platforms-container {
  width: 100%;
  padding: 16px 16px 50px;
  box-sizing: border-box;
}

.platform-list {
  display: flex;
  flex-direction: column;
  gap: 10px; /* Расстояние между карточками */
}

.platform-item {
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  padding: 10px; /* Равный отступ со всех сторон для иконки */
  gap: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: transform 0.1s ease, opacity 0.1s ease;
  touch-action: manipulation; /* главное для Telegram */
  -webkit-tap-highlight-color: rgba(0, 0, 0, 0.08);
  user-select: none;
  -webkit-user-select: none;
}

.platform-item:active {
  transform: scale(0.98);
  opacity: 0.8;
}

/* Иконка */
.icon-box {
  width: 42px;
  height: 42px;
  min-width: 42px;
  background: var(--tg-theme-bg-color);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

/* Текстовая часть */
.main-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.name {
  font-weight: 600;
  font-size: 15px;
  color: var(--tg-theme-text-color);
  line-height: 1.2;
}

.description {
  font-size: 11px;
  color: var(--tg-theme-hint-color);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Число и стрелка */
.count-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--tg-theme-hint-color);
}

.chevron {
  color: var(--tg-theme-hint-color);
  font-size: 20px;
  opacity: 0.4;
  margin-left: -4px;
}

/* Стили кнопки добавления */
.add-button {
  border: 1px dashed var(--tg-theme-button-color);
  background: transparent;
  margin-top: 8px;
}

.add-icon {
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  font-weight: bold;
}

.add-button .name {
  color: var(--tg-theme-button-color);
}

/* Вспомогательные состояния */
.status-msg {
  text-align: center;
  padding: 40px 20px;
  color: var(--tg-theme-hint-color);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--tg-theme-hint-color);
  border-top-color: var(--tg-theme-button-color);
  border-radius: 50%;
  margin: 0 auto 12px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}


/* Кнопка правки в заголовке */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 4px;
}

.title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--tg-theme-text-color);
}

.edit-mode-btn {
  background: none;
  border: none;
  color: var(--tg-theme-button-color);
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

/* Ручка для перетаскивания */
.drag-handle {
  padding: 0 8px 0 4px;
  color: var(--tg-theme-hint-color);
  font-size: 20px;
  cursor: grab;
  user-select: none;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

.platform-item.editing {
  cursor: default;
}

.platform-item:not(.editing) {
  cursor: pointer;
}

.platform-item.editing:active {
  transform: none;
}

.ghost-card {
  opacity: 0.4;
  background: var(--tg-theme-hint-color) !important;
}
</style>