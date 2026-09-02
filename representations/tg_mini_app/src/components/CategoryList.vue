<script setup>
import {ref, watch, onMounted, onUnmounted, computed} from 'vue';
import draggable from 'vuedraggable';
import {useTelegram} from '../composables/useTelegram';
import {categoryApi} from '../api/category.js';
import {accountApi} from '../api/account.js';
import {iconDisplayLabel} from '../api/customIcon.js';
import CategoryIcon from './CategoryIcon.vue';

const emit = defineEmits(['select-category', 'add-category']);
const {tg, initData} = useTelegram();
const categories = ref([]);
const isLoading = ref(true);
const error = ref(null);
const isEditMode = ref(false);

// ── Поиск ─────────────────────────────────────────────────────────────────────
const searchQuery = ref('');
const searchResults = ref([]);
const isSearching = ref(false);
const searchMode = computed(() => searchQuery.value.trim().length > 0);

let searchTimer = null;
const handleSearchInput = () => {
  clearTimeout(searchTimer);
  if (!searchQuery.value.trim()) {
    searchResults.value = [];
    return;
  }
  searchTimer = setTimeout(runSearch, 300);
};

const runSearch = async () => {
  if (!searchQuery.value.trim()) return;
  isSearching.value = true;
  try {
    searchResults.value = await accountApi.search(initData, searchQuery.value.trim());
  } catch (e) {
    tg.showAlert('Ошибка поиска');
  } finally {
    isSearching.value = false;
  }
};

const clearSearch = () => {
  searchQuery.value = '';
  searchResults.value = [];
};

// ── Swipe-to-delete state ─────────────────────────────────────────────────────
const swipeData = ref({});

// ── Кнопки ───────────────────────────────────────────────────────────────────
const onAddClick = () => emit('add-category');
const onDoneClick = () => { isEditMode.value = false; };
const onSettingsClick = () => { isEditMode.value = true; };

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
  tg.MainButton.setText('Добавить категорию');
  tg.MainButton.onClick(onAddClick);
  tg.MainButton.show();
  tg.SettingsButton.onClick(onSettingsClick);
  tg.SettingsButton.show();
};

watch(isEditMode, (val) => {
  if (val) enterEditMode();
  else exitEditMode();
});

watch(searchMode, (val) => {
  if (val) {
    tg.MainButton.hide();
    tg.SettingsButton.hide();
  } else {
    exitEditMode();
  }
});

// ── Swipe logic ───────────────────────────────────────────────────────────────
const mouseSwipeCategory = ref(null);

const swipeStart = (clientX, clientY, category, target) => {
  if (!isEditMode.value) return;
  if (target.closest('.drag-handle')) return;
  const wrapper = target.closest('.swipe-wrapper');
  const maxSwipe = wrapper ? wrapper.offsetWidth * 0.2 : 80;
  swipeData.value[category.id] = {
    startX: clientX, startY: clientY,
    currentX: 0, isSwiping: false, decided: false,
    maxSwipe, reachedLimit: false
  };
};

const swipeMove = (clientX, clientY, category, e) => {
  if (!isEditMode.value) return;
  const state = swipeData.value[category.id];
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
    if (state.currentX <= -state.maxSwipe + 1 && !state.reachedLimit) {
      state.reachedLimit = true;
      tg.HapticFeedback.impactOccurred('medium');
    } else if (state.currentX > -state.maxSwipe + 1) {
      state.reachedLimit = false;
    }
  }
};

const swipeEnd = (category) => {
  if (!isEditMode.value) return;
  const state = swipeData.value[category.id];
  if (!state) return;
  if (state.isSwiping && state.reachedLimit) {
    state.currentX = 0;
    state.isSwiping = false;
    tg.showConfirm(
        `Удалить категорию «${iconDisplayLabel(category.icon)} ${category.name}»?`,
        async (confirmed) => { if (confirmed) await deleteCategory(category); }
    );
  } else {
    state.currentX = 0;
    state.isSwiping = false;
  }
};

const onTouchStart = (e, category) => swipeStart(e.touches[0].clientX, e.touches[0].clientY, category, e.target);
const onTouchMove = (e, category) => swipeMove(e.touches[0].clientX, e.touches[0].clientY, category, e);
const onTouchEnd = (e, category) => swipeEnd(category);

const onMouseDown = (e, category) => {
  if (e.button !== 0) return;
  swipeStart(e.clientX, e.clientY, category, e.target);
  mouseSwipeCategory.value = category;
  const onMMove = (ev) => swipeMove(ev.clientX, ev.clientY, category, ev);
  const onMUp = () => {
    swipeEnd(category);
    mouseSwipeCategory.value = null;
    document.removeEventListener('mousemove', onMMove);
    document.removeEventListener('mouseup', onMUp);
  };
  document.addEventListener('mousemove', onMMove);
  document.addEventListener('mouseup', onMUp);
};

const getItemStyle = (category) => {
  if (!isEditMode.value) return {};
  const state = swipeData.value[category.id];
  const x = state?.currentX || 0;
  return {
    transform: `translateX(${x}px)`,
    transition: state?.isSwiping ? 'none' : 'transform 0.3s ease'
  };
};

const onDragStart = () => {
  tg.HapticFeedback.impactOccurred('light');
  for (const id in swipeData.value) {
    swipeData.value[id].currentX = 0;
    swipeData.value[id].isSwiping = false;
  }
};

// ── API ───────────────────────────────────────────────────────────────────────
const fetchCategories = async () => {
  try {
    const response = await categoryApi.getList(initData);
    categories.value = response.data || response;
  } catch (e) {
    tg.showAlert('Ошибка загрузки');
  }
};

const handleReorder = async () => {
  tg.HapticFeedback.impactOccurred('medium');
  try {
    const ids = categories.value.map(p => String(p.id));
    await categoryApi.reorder(initData, ids);
  } catch (e) {
    tg.showAlert('Ошибка сохранения порядка');
    await fetchCategories();
  }
};

const deleteCategory = async (category) => {
  try {
    await categoryApi.delete(initData, category.id);
    categories.value = categories.value.filter(p => p.id !== category.id);
    tg.HapticFeedback.notificationOccurred('success');
  } catch (e) {
    tg.showAlert('Ошибка удаления');
  }
};

const selectCategory = (category) => {
  if (isEditMode.value) return;
  emit('select-category', category);
};

const selectSearchResult = (result) => {
  emit('select-category', {
    id: result.category_id,
    name: result.category_name,
    icon: result.category_icon,
    _searchAccount: result,
  });
};

onMounted(async () => {
  try {
    await fetchCategories();
  } catch (e) {
    error.value = 'Не удалось загрузить данные';
  } finally {
    isLoading.value = false;
    exitEditMode();
  }
});

onUnmounted(() => {
  tg.MainButton.hide();
  tg.MainButton.offClick(onAddClick);
  tg.MainButton.offClick(onDoneClick);
  tg.SettingsButton.hide();
  tg.SettingsButton.offClick(onSettingsClick);
  clearTimeout(searchTimer);
});
</script>

<template>
  <div class="categories-container">
    <div class="header-actions">
      <h2 class="title">Категории</h2>
    </div>

    <!-- Поиск -->
    <div class="search-bar">
      <span class="search-icon">🔍</span>
      <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Поиск по всем данным..."
          @input="handleSearchInput"
      />
      <button v-if="searchQuery" class="search-clear" @click="clearSearch">✕</button>
    </div>

    <!-- Режим поиска -->
    <template v-if="searchMode">
      <div v-if="isSearching" class="status-msg">
        <div class="spinner"></div>
      </div>
      <div v-else-if="searchResults.length === 0" class="empty-state">
        <div class="empty-icon">🔍</div>
        <p>Ничего не найдено</p>
      </div>
      <div v-else class="search-results">
        <div
            v-for="result in searchResults"
            :key="result.account_id"
            class="card-item search-item"
            @click="selectSearchResult(result)"
        >
          <div class="icon-box">
            <CategoryIcon :icon="result.category_icon" fallback="🌐" size="fill" />
          </div>
          <div class="main-content">
            <div class="search-breadcrumb">
              <span v-if="result.parent_category_name" class="breadcrumb-part">{{ result.parent_category_name }}</span>
              <span v-if="result.parent_category_name" class="breadcrumb-sep">›</span>
              <span class="breadcrumb-part">{{ result.category_name }}</span>
              <span v-if="result.resource_name" class="breadcrumb-sep">›</span>
              <span v-if="result.resource_name" class="breadcrumb-resource">{{ result.resource_name }}</span>
            </div>
            <div class="search-login">{{ result.login }}</div>
            <div v-if="result.label || result.email" class="search-meta">
              <span v-if="result.label">{{ result.label }}</span>
              <span v-if="result.label && result.email"> · </span>
              <span v-if="result.email">{{ result.email }}</span>
            </div>
          </div>
          <div class="chevron">›</div>
        </div>
      </div>
    </template>

    <!-- Обычный режим -->
    <template v-else>
      <div v-if="isLoading" class="status-msg">
        <div class="spinner"></div>
        <p>Загрузка данных...</p>
      </div>

      <div v-else-if="error" class="status-msg error">
        <p>{{ error }}</p>
        <button @click="fetchCategories">Обновить</button>
      </div>

      <template v-else>
        <draggable
            v-model="categories"
            item-key="id"
            class="category-list"
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
          <template #item="{ element: category }">
            <div class="swipe-wrapper">
              <div v-if="(swipeData[category.id]?.currentX || 0) < -5"
                   class="delete-bg"
                   :class="{ 'delete-ready': swipeData[category.id]?.reachedLimit }">
                <span class="delete-icon">🗑</span>
              </div>

              <div
                  class="card-item category-item"
                  :class="{ 'editing': isEditMode }"
                  :style="getItemStyle(category)"
                  @click="!isEditMode && selectCategory(category)"
                  @contextmenu.prevent
                  @touchstart="onTouchStart($event, category)"
                  @touchmove="onTouchMove($event, category)"
                  @touchend="onTouchEnd($event, category)"
                  @mousedown="onMouseDown($event, category)"
              >
                <div class="icon-box">
                  <CategoryIcon :icon="category.icon" fallback="🌐" size="fill" />
                </div>
                <div class="main-content">
                  <div class="name">{{ category.name }}</div>
                  <div v-if="category.description" class="description">
                    {{ category.description }}
                  </div>
                </div>

                <template v-if="!isEditMode">
                  <div class="counts-col">
                    <span v-if="category.children_count > 0" class="badge-sub">{{ category.children_count }} подкат.</span>
                    <span class="count-value">{{ category.accounts_count || 0 }}</span>
                  </div>
                  <div class="chevron">›</div>
                </template>

                <div v-if="isEditMode" class="drag-handle">☰</div>
              </div>
            </div>
          </template>
        </draggable>
      </template>
    </template>
  </div>
</template>

<style scoped>
.categories-container {
  width: 100%;
  padding: 16px 16px 50px;
  box-sizing: border-box;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* ── Поиск ── */
.search-bar {
  display: flex;
  align-items: center;
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 12px;
  padding: 0 12px;
  margin-top: 8px;
  margin-bottom: 16px;
  border: 1px solid rgba(128, 128, 128, 0.15);
  gap: 8px;
}

.search-icon {
  font-size: 16px;
  opacity: 0.5;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  padding: 12px 0;
  font-size: 15px;
  color: var(--tg-theme-text-color);
}

.search-input::placeholder {
  color: var(--tg-theme-hint-color);
}

.search-clear {
  background: none;
  border: none;
  color: var(--tg-theme-hint-color);
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  flex-shrink: 0;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.search-item {
  cursor: pointer;
}

.search-breadcrumb {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 2px;
}

.breadcrumb-part {
  font-size: 12px;
  color: var(--tg-theme-hint-color);
  font-weight: 500;
}

.breadcrumb-resource {
  font-size: 12px;
  color: var(--tg-theme-button-color);
  font-weight: 500;
}

.breadcrumb-sep {
  font-size: 12px;
  color: var(--tg-theme-hint-color);
  opacity: 0.5;
}

.search-login {
  font-weight: 600;
  font-size: 15px;
  color: var(--tg-theme-text-color);
}

.search-meta {
  font-size: 11px;
  color: var(--tg-theme-hint-color);
  margin-top: 2px;
}

/* ── Inner elements ── */
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

/* ── Header ── */
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
</style>
