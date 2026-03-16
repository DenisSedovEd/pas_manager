<script setup>
    import {ref, watch, onMounted, onUnmounted} from 'vue';
    import draggable from 'vuedraggable';
    import {useTelegram} from '../composables/useTelegram';
    import {categoryApi} from '../api/category.js';

    const emit = defineEmits(['select-category', 'add-category']);
    const {tg, initData} = useTelegram();
    const categories = ref([]);
    const isLoading = ref(true);
    const error = ref(null);
    const isEditMode = ref(false);

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

    // ── Общая логика свайпа (touch + mouse) ─────────────────────────────────────
    const mouseSwipeCategory = ref(null);

    const swipeStart = (clientX, clientY, category, target) => {
      if (!isEditMode.value) return;
      if (target.closest('.drag-handle')) return;
      const wrapper = target.closest('.swipe-wrapper');
      const maxSwipe = wrapper ? wrapper.offsetWidth * 0.2 : 80;
      swipeData.value[category.id] = {
        startX: clientX,
        startY: clientY,
        currentX: 0,
        isSwiping: false,
        decided: false,
        maxSwipe,
        reachedLimit: false
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

        // Хаптик когда упёрлись в край
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
            `Удалить категорию «${category.icon} ${category.name}»?`,
            async (confirmed) => {
              if (confirmed) await deletePCategory(category);
            }
        );
      } else {
        state.currentX = 0;
        state.isSwiping = false;
      }
    };

    // ── Touch-обработчики ────────────────────────────────────────────────────────
    const onTouchStart = (e, category) => {
      swipeStart(e.touches[0].clientX, e.touches[0].clientY, category, e.target);
    };

    const onTouchMove = (e, category) => {
      swipeMove(e.touches[0].clientX, e.touches[0].clientY, category, e);
    };

    const onTouchEnd = (e, category) => {
      swipeEnd(category);
    };

    // ── Mouse-обработчики (десктоп) ──────────────────────────────────────────────
    const onMouseDown = (e, category) => {
      if (e.button !== 0) return; // только ЛКМ
      swipeStart(e.clientX, e.clientY, category, e.target);
      mouseSwipeCategory.value = category;

      const onMMove = (ev) => {
        swipeMove(ev.clientX, ev.clientY, category, ev);
      };
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

    const deletePCategory = async (category) => {
      try {
        await categoryApi.delete(initData, category.id);
        categories.value = categories.value.filter(p => p.id !== category.id);
        tg.HapticFeedback.notificationOccurred('success');
      } catch (e) {
        tg.showAlert('Ошибка удаления');
      }
    };

    const selectPCategory = (category) => {
      if (isEditMode.value) return;
      emit('select-category', category);
    };

    onMounted(async () => {
      try {
        await fetchCategories();
      } catch (e) {
        console.error('Ошибка загрузки категорий:', e);
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
    <div class="categories-container">
      <div class="header-actions">
        <h2 class="title">Категории</h2>
      </div>

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

              <!-- Фон удаления — рендерится ТОЛЬКО когда карточка реально сдвинута -->
              <div v-if="(swipeData[category.id]?.currentX || 0) < -5"
                   class="delete-bg"
                   :class="{ 'delete-ready': swipeData[category.id]?.reachedLimit }">
                <span class="delete-icon">🗑</span>
              </div>

              <div
                  class="card-item category-item"
                  :class="{ 'editing': isEditMode }"
                  :style="getItemStyle(category)"
                  @click="!isEditMode && selectPCategory(category)"
                  @contextmenu.prevent
                  @touchstart="onTouchStart($event, category)"
                  @touchmove="onTouchMove($event, category)"
                  @touchend="onTouchEnd($event, category)"
                  @mousedown="onMouseDown($event, category)"
              >
                <div class="icon-box">{{ category.icon || '🌐' }}</div>
                <div class="main-content">
                  <div class="name">{{ category.name }}</div>
                  <div v-if="category.description" class="description">
                    {{ category.description }}
                  </div>
                </div>

                <template v-if="!isEditMode">
                  <div class="count-value">{{ category.accounts_count || 0 }}</div>
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
  </style>