<script setup>
import {ref, watch, onMounted} from 'vue';
import draggable from 'vuedraggable';
import {useTelegram} from '../composables/useTelegram';
import {platformApi} from '../api/platform.js';

const emit = defineEmits(['select-platform', 'add-platform']);
const {tg, initData} = useTelegram();
const platforms = ref([]);
const isLoading = ref(true);
const error = ref(null);
const isEditMode = ref(false);

// ── Swipe-to-delete state ─────────────────────────────────────────────────────
const swipeData = ref({});

watch(isEditMode, (val) => {
  if (!val) swipeData.value = {};
});

// ── Общая логика свайпа (touch + mouse) ─────────────────────────────────────
const mouseSwipePlatform = ref(null);

const swipeStart = (clientX, clientY, platform, target) => {
  if (!isEditMode.value) return;
  if (target.closest('.drag-handle')) return;
  swipeData.value[platform.id] = {
    startX: clientX,
    startY: clientY,
    currentX: 0,
    isSwiping: false,
    decided: false
  };
};

const swipeMove = (clientX, clientY, platform, e) => {
  if (!isEditMode.value) return;
  const state = swipeData.value[platform.id];
  if (!state) return;

  const dx = clientX - state.startX;
  const dy = clientY - state.startY;

  if (!state.decided) {
    if (Math.abs(dx) > 8 || Math.abs(dy) > 8) {
      state.decided = true;
      state.isSwiping = Math.abs(dx) > Math.abs(dy) && dx < 0;
    }
    return;
  }

  if (state.isSwiping) {
    e.preventDefault();
    e.stopPropagation();
    state.currentX = Math.min(0, dx);
  }
};

const swipeEnd = (platform) => {
  if (!isEditMode.value) return;
  const state = swipeData.value[platform.id];
  if (!state) return;

  if (state.isSwiping && state.currentX < -80) {
    state.currentX = 0;
    state.isSwiping = false;
    tg.showConfirm(
      `Удалить платформу «${platform.name}»?`,
      async (confirmed) => {
        if (confirmed) await deletePlatform(platform);
      }
    );
  } else {
    state.currentX = 0;
    state.isSwiping = false;
  }
};

// ── Touch-обработчики ────────────────────────────────────────────────────────
const onTouchStart = (e, platform) => {
  swipeStart(e.touches[0].clientX, e.touches[0].clientY, platform, e.target);
};

const onTouchMove = (e, platform) => {
  swipeMove(e.touches[0].clientX, e.touches[0].clientY, platform, e);
};

const onTouchEnd = (e, platform) => {
  swipeEnd(platform);
};

// ── Mouse-обработчики (десктоп) ──────────────────────────────────────────────
const onMouseDown = (e, platform) => {
  if (e.button !== 0) return; // только ЛКМ
  swipeStart(e.clientX, e.clientY, platform, e.target);
  mouseSwipePlatform.value = platform;

  const onMMove = (ev) => {
    swipeMove(ev.clientX, ev.clientY, platform, ev);
  };
  const onMUp = () => {
    swipeEnd(platform);
    mouseSwipePlatform.value = null;
    document.removeEventListener('mousemove', onMMove);
    document.removeEventListener('mouseup', onMUp);
  };
  document.addEventListener('mousemove', onMMove);
  document.addEventListener('mouseup', onMUp);
};

const getItemStyle = (platform) => {
  if (!isEditMode.value) return {};
  const state = swipeData.value[platform.id];
  const x = state?.currentX || 0;
  return {
    transform: `translateX(${x}px)`,
    transition: state?.isSwiping ? 'none' : 'transform 0.3s ease'
  };
};

// ── Drag start — сбрасываем все swipe-состояния ───────────────────────────────
const onDragStart = () => {
  tg.HapticFeedback.impactOccurred('light');
  // Сбрасываем все свайпы чтобы delete-bg не рендерился в клоне
  for (const id in swipeData.value) {
    swipeData.value[id].currentX = 0;
    swipeData.value[id].isSwiping = false;
  }
};

// ── API ───────────────────────────────────────────────────────────────────────
const fetchPlatforms = async () => {
  try {
    const response = await platformApi.getList(initData);
    platforms.value = response.data || response;
  } catch (e) {
    tg.showAlert('Ошибка загрузки');
  }
};

const handleReorder = async () => {
  tg.HapticFeedback.impactOccurred('medium');
  try {
    const ids = platforms.value.map(p => String(p.id));
    await platformApi.reorder(initData, ids);
  } catch (e) {
    tg.showAlert('Ошибка сохранения порядка');
    await fetchPlatforms();
  }
};

const deletePlatform = async (platform) => {
  try {
    await platformApi.delete(initData, platform.id);
    platforms.value = platforms.value.filter(p => p.id !== platform.id);
    tg.HapticFeedback.notificationOccurred('success');
  } catch (e) {
    tg.showAlert('Ошибка удаления');
  }
};

const selectPlatform = (platform) => {
  if (isEditMode.value) return;
  emit('select-platform', platform);
};

onMounted(async () => {
  try {
    await fetchPlatforms();
  } catch (e) {
    console.error('Ошибка загрузки платформ:', e);
    error.value = 'Не удалось загрузить данные';
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
          :animation="200"
          :force-fallback="true"
          :delay="300"
          :delay-on-touch-only="true"
          @start="onDragStart"
          @end="handleReorder"
      >
        <template #item="{ element: platform }">
          <div class="swipe-wrapper">

            <!-- Красный фон — рендерится ТОЛЬКО когда карточка реально сдвинута -->
            <div v-if="(swipeData[platform.id]?.currentX || 0) < -5" class="delete-bg">
              <span class="delete-icon">🗑</span>
              <span class="delete-label">Удалить</span>
            </div>

            <div
                class="platform-item"
                :class="{ 'editing': isEditMode }"
                :style="getItemStyle(platform)"
                @click="!isEditMode && selectPlatform(platform)"
                @contextmenu.prevent
                @touchstart="onTouchStart($event, platform)"
                @touchmove="onTouchMove($event, platform)"
                @touchend="onTouchEnd($event, platform)"
                @mousedown="onMouseDown($event, platform)"
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
  gap: 10px;
}

/* ── Swipe wrapper ──────────────────────────────────── */
.swipe-wrapper {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
}

.delete-bg {
  position: absolute;
  inset: 0;
  background: #ff3b30;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 20px;
  gap: 6px;
  color: #fff;
  font-weight: 600;
  pointer-events: none;
}

.delete-icon {
  font-size: 18px;
}

.delete-label {
  font-size: 14px;
}

/* ── Platform item ──────────────────────────────────── */
.platform-item {
  position: relative;
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  padding: 10px;
  gap: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: rgba(0, 0, 0, 0.08);
  user-select: none;
  -webkit-user-select: none;
}

.platform-item:active {
  transform: scale(0.98);
  opacity: 0.8;
}

.platform-item.editing {
  cursor: default;
  touch-action: pan-y;
}

.platform-item.editing:active {
  transform: none;
  opacity: 1;
}

.platform-item:not(.editing) {
  cursor: pointer;
}

/* ── Inner elements ─────────────────────────────────── */

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

/* ── Header ─────────────────────────────────────────── */
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

.drag-handle {
  padding: 0 8px 0 4px;
  color: var(--tg-theme-hint-color);
  font-size: 20px;
  cursor: grab;
  user-select: none;
  touch-action: none;
  -webkit-tap-highlight-color: transparent;
}
</style>