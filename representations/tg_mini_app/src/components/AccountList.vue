<script setup>
import {ref, watch, onMounted, onUnmounted, computed} from 'vue';
import draggable from 'vuedraggable';
import {useTelegram} from '../composables/useTelegram';
import {accountApi} from '../api/account.js';
import {categoryApi} from '../api/category.js';

const emit = defineEmits(['select-account', 'add-account', 'edit-category']);
const {tg, initData} = useTelegram();

const accounts = ref([]);
const subcategories = ref([]);
const subAccounts = ref({});
const expandedSubIds = ref({});
const subLoadingIds = ref({});
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

watch(isEditMode, async (val) => {
  if (val) {
    await expandAllSubcategories();
    enterEditMode();
  } else {
    exitEditMode();
  }
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

const findSubcategoryId = (accountId) => {
  for (const [subId, list] of Object.entries(subAccounts.value)) {
    if (list.some(a => a.id === accountId)) return subId;
  }
  return null;
};

const swipeEnd = (account) => {
  if (!isEditMode.value) return;
  const state = swipeData.value[account.id];
  if (!state) return;

  if (state.isSwiping && state.reachedLimit) {
    state.currentX = 0;
    state.isSwiping = false;
    const subId = findSubcategoryId(account.id);
    tg.showConfirm(
        `Удалить аккаунт «${account.label || account.login}»?`,
        async (confirmed) => {
          if (confirmed) await deleteAccount(account, subId);
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
    const [accountsResp, childrenResp] = await Promise.all([
      accountApi.getList(initData, props.categoryId),
      categoryApi.getChildren(initData, props.categoryId),
    ]);
    accounts.value = accountsResp.data || accountsResp;
    subcategories.value = childrenResp.data || childrenResp;
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

const handleSubReorder = async (subId) => {
  tg.HapticFeedback.impactOccurred('medium');
  try {
    const ids = (subAccounts.value[subId] || []).map(a => String(a.id));
    await accountApi.reorder(initData, ids);
  } catch (e) {
    tg.showAlert('Ошибка сохранения порядка');
    await loadSubAccounts(subId, true);
  }
};

const expandAllSubcategories = async () => {
  const nextExpanded = {...expandedSubIds.value};
  for (const sub of subcategories.value) {
    nextExpanded[sub.id] = true;
    await loadSubAccounts(sub.id);
  }
  expandedSubIds.value = nextExpanded;
};

const deleteAccount = async (account, subId = null) => {
  try {
    await accountApi.delete(initData, account.id);
    if (subId) {
      subAccounts.value = {
        ...subAccounts.value,
        [subId]: subAccounts.value[subId].filter(a => a.id !== account.id),
      };
    } else {
      accounts.value = accounts.value.filter(a => a.id !== account.id);
    }
    tg.HapticFeedback.notificationOccurred('success');
  } catch (e) {
    tg.showAlert('Ошибка удаления');
  }
};

const loadSubAccounts = async (subId, force = false) => {
  if (!force && subAccounts.value[subId]) return;
  subLoadingIds.value = {...subLoadingIds.value, [subId]: true};
  try {
    const resp = await accountApi.getList(initData, subId);
    subAccounts.value = {...subAccounts.value, [subId]: resp.data || resp};
  } catch (e) {
    tg.showAlert('Ошибка загрузки аккаунтов подкатегории');
  } finally {
    const next = {...subLoadingIds.value};
    delete next[subId];
    subLoadingIds.value = next;
  }
};

const toggleSubcategory = async (sub) => {
  if (isEditMode.value) return;
  const subId = sub.id;
  if (expandedSubIds.value[subId]) {
    expandedSubIds.value = {...expandedSubIds.value, [subId]: false};
    return;
  }
  tg.HapticFeedback.impactOccurred('light');
  expandedSubIds.value = {...expandedSubIds.value, [subId]: true};
  await loadSubAccounts(subId);
};

const selectAccount = (account, subCategory = null) => {
  if (isEditMode.value) return;
  emit('select-account', account, subCategory);
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
          <h1>{{ props.category?.name || 'Категория' }}</h1>
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
      <!-- Подкатегории -->
      <div v-if="subcategories.length > 0" class="subcategories-block">
        <div class="subcategories-label">Подкатегории</div>
        <div
            v-for="sub in subcategories"
            :key="sub.id"
            class="subcategory-group"
        >
          <div
              class="card-item subcategory-item"
              :class="{ expanded: expandedSubIds[sub.id] }"
              @click="toggleSubcategory(sub)"
          >
            <div class="icon-box">{{ sub.icon || '📁' }}</div>
            <div class="main-content">
              <div class="name">{{ sub.name }}</div>
              <div v-if="sub.description" class="description">{{ sub.description }}</div>
            </div>
            <div class="counts-col">
              <span class="count-value">{{ sub.accounts_count || 0 }}</span>
            </div>
            <button
                class="sub-edit-btn"
                @click.stop="$emit('edit-category', sub)"
            >⚙️</button>
            <div class="chevron expand-chevron" :class="{ open: expandedSubIds[sub.id] }">›</div>
          </div>

          <div v-if="expandedSubIds[sub.id]" class="sub-accounts">
            <div v-if="subLoadingIds[sub.id]" class="sub-status">Загрузка...</div>
            <div v-else-if="!(subAccounts[sub.id] || []).length" class="sub-status">Нет аккаунтов</div>
            <draggable
                v-else
                :model-value="subAccounts[sub.id]"
                @update:model-value="(list) => { subAccounts[sub.id] = list }"
                item-key="id"
                class="sub-accounts-list"
                handle=".drag-handle"
                :disabled="!isEditMode"
                ghost-class="ghost-card"
                :animation="200"
                :force-fallback="true"
                :delay="300"
                :delay-on-touch-only="true"
                @start="onDragStart"
                @end="() => handleSubReorder(sub.id)"
            >
              <template #item="{ element: account }">
                <div class="swipe-wrapper sub-account-wrapper">
                  <div v-if="(swipeData[account.id]?.currentX || 0) < -5"
                       class="delete-bg"
                       :class="{ 'delete-ready': swipeData[account.id]?.reachedLimit }">
                    <span class="delete-icon">🗑</span>
                  </div>
                  <div
                      class="card-item account-item sub-account-item"
                      :class="{ 'editing': isEditMode }"
                      :style="getItemStyle(account)"
                      @click="!isEditMode && selectAccount(account, sub)"
                      @contextmenu.prevent
                      @touchstart="onTouchStart($event, account)"
                      @touchmove="onTouchMove($event, account)"
                      @touchend="onTouchEnd($event, account)"
                      @mousedown="onMouseDown($event, account)"
                  >
                    <div class="icon-box">{{ sub.icon || '👤' }}</div>
                    <div class="main-content">
                      <div class="top-row">
                        <span class="resource-text">
                          {{ resourceMap[account.resource_id]?.resource_name || '-' }}
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
          </div>
        </div>
      </div>

      <div v-if="accounts.length === 0 && subcategories.length === 0 && !isEditMode" class="empty-state">
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
                @click="!isEditMode && selectAccount(account, null)"
                @contextmenu.prevent
                @touchstart="onTouchStart($event, account)"
                @touchmove="onTouchMove($event, account)"
                @touchend="onTouchEnd($event, account)"
                @mousedown="onMouseDown($event, account)"
            >
              <div class="icon-box">{{ props.category?.icon || '👤' }}</div>

              <div class="main-content">
                <div class="top-row">
                  <span class="resource-text">
                    {{ resourceMap[account.resource_id]?.resource_name || '-' }}
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

/* ── Подкатегории ── */
.subcategories-block {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.subcategories-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--tg-theme-hint-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0 4px;
  margin-bottom: 4px;
}

.subcategory-group {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.subcategory-item {
  cursor: pointer;
}

.subcategory-item.expanded {
  background: rgba(128, 128, 128, 0.08);
}

.sub-edit-btn {
  background: none;
  border: none;
  font-size: 16px;
  padding: 4px 6px;
  cursor: pointer;
  opacity: 0.7;
  flex-shrink: 0;
  line-height: 1;
}

.sub-edit-btn:active {
  opacity: 1;
}

.expand-chevron {
  transition: transform 0.2s ease;
}

.expand-chevron.open {
  transform: rotate(90deg);
}

.sub-accounts {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 0 8px 12px;
}

.sub-accounts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sub-account-wrapper {
  margin-left: 8px;
}

.sub-account-item {
  opacity: 0.95;
}

.sub-status {
  padding: 8px 12px 8px 20px;
  font-size: 13px;
  color: var(--tg-theme-hint-color);
}

.counts-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.badge-sub {
  font-size: 10px;
  color: var(--tg-theme-button-color);
  font-weight: 500;
  white-space: nowrap;
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
}
</style>