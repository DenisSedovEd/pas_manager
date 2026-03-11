<script setup>
import { ref, onMounted } from 'vue';
import { useTelegram } from '../composables/useTelegram';
import { platformApi } from '../api/platform.js';

const emit = defineEmits(['select-platform', 'add-platform']);
const { tg, initData } = useTelegram();
const platforms = ref([]);
const isLoading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    platforms.value = await platformApi.getList(initData);
  } catch (e) {
    console.error("Ошибка загрузки платформ:", e);
    error.value = "Не удалось загрузить платформы";
    tg.showAlert("Ошибка загрузки платформ");
  } finally {
    isLoading.value = false;
  }
});
</script>
<template>
  <div class="platforms-container">
    <div v-if="isLoading" class="loader">Загрузка платформ...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <div class="platform-grid">
        <div
          v-for="platform in platforms"
          :key="platform.id"
          class="platform-card"
          @click="emit('select-platform', platform)"
        >
          <div class="platform-content">
            <div class="icon-box">{{ platform.icon || '🌐'}}</div>
            <div class="info">
              <div class="name">{{ platform.name }}</div>
              <div class="count">{{ platform.accounts_count }} аккаунтов</div>
            </div>
          </div>
        </div>
      </div>

      <button class="add-btn" @click="emit('add-platform')">+ Добавить платформу</button>
    </template>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
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

.error {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #ff6b6b;
  text-align: center;
  padding: 20px;
}

.platform-grid {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  padding: 16px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  width: 100%;
  align-content: start;
}

.platform-card {
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 16px;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: transform 0.1s ease;
  overflow: hidden;
}

.platform-card:active {
  transform: scale(0.95);
}

.platform-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  gap: 12px;
  text-align: center;
  min-width: 0;
}

.icon-box {
  font-size: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--tg-theme-bg-color);
  border-radius: 12px;
}

.info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  min-width: 0;
}

.name {
  font-weight: 600;
  font-size: 14px;
  color: var(--tg-theme-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.count {
  font-size: 11px;
  color: var(--tg-theme-hint-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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