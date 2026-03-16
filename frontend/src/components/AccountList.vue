<script setup>
import {ref, watch, onMounted, onUnmounted, computed} from 'vue';
import draggable from 'vuedraggable';
import {useTelegram} from '../composables/useTelegram';
import {accountApi} from '../api/account.js';

const emit = defineEmits(['select-account', 'add-account', 'edit-category']);
const {tg, initData} = useTelegram();

const accounts = ref([]);
const isLoading = ref(true);
const error = ref(null);
const isEditMode = ref(false);

const props = defineProps({
  categoryId: String,
  category: Object,
  resources: {type: Array, default: () => []}
});

// ── Swipe-to-delete state ─────────────────────────────────────────────────────
const swipeData = ref({});

// ── Кнопки ───────────────────────────────────────────────────────────────────
const onAddClick = () => emit('add-account');
const onDoneClick = () => {
  isEditMode.value = false;
};
const onSettingsClick = () => {
  isEditMode.value = true;
};

const resourceMap = computed(() =>
    Object.fromEntries(props.resources.map(r => [r.id, r]))
);

const enterEditMode = () => {
  tg.MainButton.offClick(onAddClick);
  tg.MainButton.setText('Готово');
  tg.MainButton.onClick(onDoneClick);
  tg.MainButton.show();
  tg.SettingsButton.offClick(onSettingsClick);
  tg.SettingsButton.hide();
};

const exitEditMode = () => {
  swipeData.value = {};
  tg.MainButton.offClick(onDoneClick);
  tg.MainButton.setText('Добавить аккаунт');
  tg.MainButton.onClick(onAddClick);
  tg.MainButton.show();
  tg.SettingsButton.onClick(onSettingsClick);
  tg.SettingsButton.show();
};

watch(isEditMode, (val) => {
  if (val) enterEditMode();
  else exitEditMode();
});

// ── Общая логика свайпа (touch + mouse) ─────────────────────────────────────
const mouseSwipeAccount = ref(null);

const swipeStart = (clientX, clientY, account, target) => {
  if (!isEditMode.value) return;
  if (target.closest('.drag-handle')) return;
  const wrapper = target.closest('.swipe-wrapper');
  const maxSwipe = wrapper ? wrapper.offsetWidth * 0.2 : 80;
  swipeData.value[account.id] = {
    startX: clientX,
    startY: clientY,
    currentX: 0,
    isSwiping: false,
    decided: false,
    maxSwipe,
    reachedLimit: false
  };
};

const swipeMove = (clientX, clientY, account, e) => {
  if (!isEditMode.value) return;
  const state = swipeData.value[account.id];
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
    state.currentX = Math.max(-state.maxSwipe, Math.min(0, dx));

    // Хаптик когда упёрлись в край
    if (state.currentX <= -state.maxSwipe + 1 && !state.reachedLimit) {
      state.reachedLimit = true;
      tg.HapticFeedback.impactOccurred('medium');
    } else if (state.currentX > -state.maxSwipe + 1) {
      state.reachedLimit = false;
    }
  }
};

const swipeEnd = (account) => {
  if (!isEditMode.value) return;
  const state = swipeData.value[account.id];
  if (!state) return;

  if (state.isSwiping && state.reachedLimit) {
    state.currentX = 0;
    state.isSwiping = false;
    tg.showConfirm(
        `Удалить аккаунт «${account.label || account.login}»?`,
        async (confirmed) => {
          if (confirmed) await deleteAccount(account);
        }
    );
  } else {
    state.currentX = 0;
    state.isSwiping = false;
  }
};

// ── Touch-обработчики ────────────────────────────────────────────────────────
const onTouchStart = (e, account) => {
  swipeStart(e.touches[0].clientX, e.touches[0].clientY, account, e.target);
};

const onTouchMove = (e, account) => {
  swipeMove(e.touches[0].clientX, e.touches[0].clientY, account, e);
};

const onTouchEnd = (e, account) => {
  swipeEnd(account);
};

// ── Mouse-обработчики (десктоп) ──────────────────────────────────────────────
const onMouseDown = (e, account) => {
  if (e.button !== 0) return;
  swipeStart(e.clientX, e.clientY, account, e.target);
  mouseSwipeAccount.value = account;

  const onMMove = (ev) => {
    swipeMove(ev.clientX, ev.clientY, account, ev);
  };
  const onMUp = () => {
    swipeEnd(account);
    mouseSwipeAccount.value = null;
    document.removeEventListener('mousemove', onMMove);
    document.removeEventListener('mouseup', onMUp);
  };
  document.addEventListener('mousemove', onMMove);
  document.addEventListener('mouseup', onMUp);
};

const getItemStyle = (account) => {
  if (!isEditMode.value) return {};
  const state = swipeData.value[account.id];
  const x = state?.currentX || 0;
  return {
    transform: `translateX(${x}px)`,
    transition: state?.isSwiping ? 'none' : 'transform 0.3s ease'
  };
};

// ── Drag start — сбрасываем все swipe-состояния ───────────────────────────────
const onDragStart = () => {
  tg.HapticFeedback.impactOccurred('light');
  for (const id in swipeData.value) {
    swipeData.value[id].currentX = 0;
    swipeData.value[id].isSwiping = false;
  }
};

// ── API ───────────────────────────────────────────────────────────────────────
const fetchAccounts = async () => {
  try {
    const response = await accountApi.getList(initData, props.categoryId);
    accounts.value = response.data || response;
  } catch (e) {
    console.error("Ошибка загрузки:", e);
    error.value = "Не удалось загрузить аккаунты";
  }
};

const handleReorder = async () => {
  tg.HapticFeedback.impactOccurred('medium');
  try {
    const ids = accounts.value.map(a => String(a.id));
    await accountApi.reorder(initData, ids);
  } catch (e) {
    tg.showAlert('Ошибка сохранения порядка');
    await fetchAccounts();
  }
};

const deleteAccount = async (account) => {
  try {
    await accountApi.delete(initData, account.id);
    accounts.value = accounts.value.filter(a => a.id !== account.id);
    tg.HapticFeedback.notificationOccurred('success');
  } catch (e) {
    tg.showAlert('Ошибка удаления');
  }
};

const selectAccount = (account) => {
  if (isEditMode.value) return;
  emit('select-account', account);
};

onMounted(async () => {
  try {
    await fetchAccounts();
  } catch (e) {
    console.error('Ошибка загрузки аккаунтов:', e);
    error.value = 'Не удалось загрузить данные';
  } finally {
    isLoading.value = false;
    exitEditMode(); // устанавливает начальное состояние кнопок
  }
});

onUnmounted(() => {
  tg.MainButton.hide();
  tg.MainButton.offClick(onAddClick);
  tg.MainButton.offClick(onDoneClick);
  tg.SettingsButton.hide();
  tg.SettingsButton.offClick(onSettingsClick);
});
</script>

<template>
  <div class="accounts-container">
    <div class="category-header">
      <div
          class="category-info"
          :class="{ 'category-info--tappable': props.category?.name !== 'Other' }"
          @click="props.category?.name !== 'Other' && $emit('edit-category', props.category)"
      >
        <span class="category-icon">{{ props.category?.icon || '🌐' }}</span>
        <div class="category-text">
          <h1>{{ props.category?.name || 'Платформа' }}</h1>
          <p v-if="props.category?.description" class="category-desc">
            {{ props.category.description }}
          </p>
        </div>
        <span v-if="props.category?.name !== 'Other'" class="header-chevron">›</span>
      </div>
    </div>

    <div v-if="isLoading" class="status-msg">
      <div class="spinner"></div>
      <p>Загрузка данных...</p>
    </div>

    <div v-else-if="error" class="status-msg error">
      <p>{{ error }}</p>
    </div>

    <template v-else>
      <div v-if="accounts.length === 0 && !isEditMode" class="empty-state">
        <div class="empty-icon">📂</div>
        <p>В этой категории пока нет аккаунтов</p>
      </div>

      <draggable
          v-model="accounts"
          item-key="id"
          class="accounts-list"
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
        <template #item="{ element: account }">
          <div class="swipe-wrapper">

            <!-- Фон удаления — рендерится ТОЛЬКО когда карточка реально сдвинута -->
            <div v-if="(swipeData[account.id]?.currentX || 0) < -5"
                 class="delete-bg"
                 :class="{ 'delete-ready': swipeData[account.id]?.reachedLimit }">
              <span class="delete-icon">🗑</span>
            </div>

            <div
                class="card-item account-item"
                :class="{ 'editing': isEditMode }"
                :style="getItemStyle(account)"
                @click="!isEditMode && selectAccount(account)"
                @contextmenu.prevent
                @touchstart="onTouchStart($event, account)"
                @touchmove="onTouchMove($event, account)"
                @touchend="onTouchEnd($event, account)"
                @mousedown="onMouseDown($event, account)"
            >
              <div class="icon-box">{{ categoryIcon || '👤' }}</div>

              <div class="main-content">
                <div class="top-row">
                  <span class="resource-text">
                    {{ resourceMap[account.resource_id]?.resource_name || '' }}
                  </span>
                  <span v-if="account.label" class="label-text">{{ account.label }}</span>
                </div>
                <div class="login-text">{{ account.login }}</div>
              </div>

              <template v-if="!isEditMode">
                <div class="chevron">›</div>
              </template>

              <div v-if="isEditMode" class="drag-handle">☰</div>
            </div>

          </div>
        </template>
      </draggable>
    </template>
  </div>
</template>

<style scoped>
.accounts-container {
  width: 100%;
  padding: 16px 16px 50px;
  box-sizing: border-box;
}

.accounts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
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
  font-size: 22px;
}

.label-text {
  font-weight: 400;
  font-size: 12px;
  color: var(--tg-theme-text-color);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.top-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
  white-space: nowrap;
  overflow: hidden;
}

.resource-text {
  font-weight: 600;
  font-size: 15px;
  color: var(--tg-theme-text-color);
  flex-shrink: 0;
}

.login-text {
  font-size: 11px;
  color: var(--tg-theme-hint-color);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chevron {
  color: var(--tg-theme-hint-color);
  font-size: 20px;
  opacity: 0.4;
}

/* ── Header ─────────────────────────────────────────── */
.category-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  background: var(--tg-theme-bg-color);
  border-bottom: 2px solid rgba(128, 128, 128, 0.2);
  margin-bottom: 30px;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.category-info--tappable {
  cursor: pointer;
  border-radius: 12px;
  padding: 4px 6px 4px 0;
  margin: -4px 0 -4px 0;
  transition: opacity 0.15s ease;
  -webkit-tap-highlight-color: rgba(0, 0, 0, 0.08);
}

.category-info--tappable:active {
  opacity: 0.7;
}

.header-chevron {
  color: var(--tg-theme-hint-color);
  font-size: 22px;
  opacity: 0.4;
  flex-shrink: 0;
  margin-left: auto;
}

.category-icon {
  font-size: 32px;
  width: 52px;
  height: 52px;
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.category-text h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--tg-theme-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-desc {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: var(--tg-theme-hint-color);
  line-height: 1.3;
}
</style>