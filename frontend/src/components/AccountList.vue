<script setup>
import {ref, watch, onMounted} from 'vue';
import draggable from 'vuedraggable';
import {useTelegram} from '../composables/useTelegram';
import {accountApi} from '../api/account.js';

const emit = defineEmits(['select-account', 'add-account', 'edit-platform']);
const {tg, initData} = useTelegram();

const accounts = ref([]);
const isLoading = ref(true);
const error = ref(null);
const isEditMode = ref(false);

const props = defineProps({
  platformId: String,
  platform: Object
});

// ── Swipe-to-delete state ─────────────────────────────────────────────────────
const swipeData = ref({});

watch(isEditMode, (val) => {
  if (!val) swipeData.value = {};
});

// ── Общая логика свайпа (touch + mouse) ─────────────────────────────────────
const mouseSwipeAccount = ref(null);

const swipeStart = (clientX, clientY, account, target) => {
  if (!isEditMode.value) return;
  if (target.closest('.drag-handle')) return;
  swipeData.value[account.id] = {
    startX: clientX,
    startY: clientY,
    currentX: 0,
    isSwiping: false,
    decided: false
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
    state.currentX = Math.min(0, dx);
  }
};

const swipeEnd = (account) => {
  if (!isEditMode.value) return;
  const state = swipeData.value[account.id];
  if (!state) return;

  if (state.isSwiping && state.currentX < -80) {
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
    const response = await accountApi.getList(initData, props.platformId);
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
  }
});
</script>

<template>
  <div class="accounts-container">
    <div class="platform-header">
      <div class="platform-info">
        <span class="platform-icon">{{ props.platform?.icon || '🌐' }}</span>
        <div class="platform-text">
          <h1>{{ props.platform?.name || 'Платформа' }}</h1>
          <p v-if="props.platform?.description" class="platform-desc">
            {{ props.platform.description }}
          </p>
        </div>
      </div>

      <div class="header-buttons">
        <button
            class="edit-mode-btn"
            @click="isEditMode = !isEditMode"
            @touchend.prevent="isEditMode = !isEditMode"
        >
          {{ isEditMode ? 'Готово' : 'Правка' }}
        </button>
        <button
            v-if="props.platform?.name !== 'Other'"
            class="edit-platform-btn"
            @click="$emit('edit-platform', props.platform)"
        >
          ✏️
        </button>
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

            <!-- Красный фон — рендерится ТОЛЬКО когда карточка реально сдвинута -->
            <div v-if="(swipeData[account.id]?.currentX || 0) < -5" class="delete-bg">
              <span class="delete-icon">🗑</span>
              <span class="delete-label">Удалить</span>
            </div>

            <div
                class="account-item"
                :class="{ 'editing': isEditMode }"
                :style="getItemStyle(account)"
                @click="!isEditMode && selectAccount(account)"
                @contextmenu.prevent
                @touchstart="onTouchStart($event, account)"
                @touchmove="onTouchMove($event, account)"
                @touchend="onTouchEnd($event, account)"
                @mousedown="onMouseDown($event, account)"
            >
              <div class="icon-box">{{ platformIcon || '👤' }}</div>

              <div class="main-content">
                <div v-if="account.label" class="label-text">{{ account.label }}</div>
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

      <div v-if="!isEditMode" class="account-item add-button" @click="emit('add-account')">
        <div class="icon-box add-icon">+</div>
        <div class="main-content">
          <div class="label-text">Add New Account</div>
          <div class="login-text">Save credentials for this platform</div>
        </div>
      </div>
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

/* ── Account item ──────────────────────────────────── */
.account-item {
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

.account-item:active {
  transform: scale(0.98);
  opacity: 0.8;
}

.account-item.editing {
  cursor: default;
  touch-action: pan-y;
}

.account-item.editing:active {
  transform: none;
  opacity: 1;
}

.account-item:not(.editing) {
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
  font-size: 22px;
}

.label-text {
  font-weight: 600;
  font-size: 15px;
  color: var(--tg-theme-text-color);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
.platform-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  background: var(--tg-theme-bg-color);
  border-bottom: 2px solid rgba(128, 128, 128, 0.2);
  margin-bottom: 30px;
}

.platform-info {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.platform-icon {
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

.platform-text h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--tg-theme-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.platform-desc {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: var(--tg-theme-hint-color);
  line-height: 1.3;
}

.header-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
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

.edit-platform-btn {
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.edit-platform-btn:active {
  opacity: 0.85;
  transform: scale(0.95);
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