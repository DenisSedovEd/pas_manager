<script setup>
import { ref, onMounted } from 'vue';
import { useTelegram } from '../composables/useTelegram';
import { vaultApi } from '../api/vault';

const { initData } = useTelegram();
const platforms = ref([]);
const isLoading = ref(true);

onMounted(async () => {
  try {
    platforms.value = await vaultApi.getPlatforms(initData);
  } catch (e) {
    console.error(e);
  } finally {
    isLoading.value = false;
  }
});
</script>
<template>
  <div class="platforms-container">
    <div v-if="isLoading" class="loader">Загрузка платформ...</div>

    <template v-else>
      <div class="platform-grid">
        <div
          v-for="platform in platforms"
          :key="platform.id"
          class="platform-card"
          @click="$emit('select-platform', platform)"
        >
          <div class="platform-content">
            <div class="icon-box">{{ platform.icon }}</div>
            <div class="info">
              <div class="name">{{ platform.name }}</div>
              <div class="count">{{ platform.accounts_count }} аккаунтов</div>
            </div>
            <div class="arrow">›</div>
          </div>
        </div>
      </div>

      <button class="add-btn">+ Добавить платформу</button>
    </template>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box; /* Важно для точного расчета ширины */
}

.platforms-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  background: var(--tg-theme-bg-color);
  overflow: hidden;
  width: 100%;
}

.loader {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: var(--tg-theme-hint-color);
}

.platform-grid {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden; /* Убираем горизонтальный скролл */
  -webkit-overflow-scrolling: touch;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%; /* Убедимся, что берет всю ширину */
}

.platform-card {
  width: 100%;
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 16px;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
  min-width: 0; /* Важно для предотвращения переполнения */
}

.platform-content {
  display: flex;
  align-items: center;
  padding: 16px;
  gap: 16px;
  min-width: 0; /* Предотвращает переполнение */
}

.icon-box {
  font-size: 24px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--tg-theme-bg-color);
  border-radius: 12px;
  flex-shrink: 0;
}

.info {
  flex-grow: 1;
  min-width: 0;
  overflow: hidden; /* Обрезаем переполняющийся контент */
}

.name {
  font-weight: 600;
  font-size: 16px;
  color: var(--tg-theme-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.count {
  font-size: 12px;
  color: var(--tg-theme-hint-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.arrow {
  color: var(--tg-theme-hint-color);
  font-size: 20px;
  font-weight: bold;
  flex-shrink: 0;
}

.add-btn {
  flex-shrink: 0;
  background: var(--tg-theme-secondary-bg-color);
  border: 2px dashed var(--tg-theme-hint-color);
  color: var(--tg-theme-hint-color);
  padding: 16px;
  border-radius: 16px;
  font-weight: 600;
  cursor: pointer;
  margin: 16px;
  width: calc(100% - 32px);
  transition: opacity 0.2s;
}

.add-btn:active {
  opacity: 0.7;
}
</style>