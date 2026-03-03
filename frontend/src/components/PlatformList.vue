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

    <div v-else class="platform-grid">
      <div
        v-for="platform in platforms"
        :key="platform.id"
        class="platform-card"
        @click="$emit('select-platform', platform)"
      >
        <div class="icon">{{ platform.icon }}</div>
        <div class="info">
          <div class="name">{{ platform.name }}</div>
          <div class="count">{{ platform.accounts_count }} аккаунтов</div>
        </div>
        <div class="arrow">›</div>
      </div>
    </div>

    <button class="add-btn">+ Добавить платформу</button>
  </div>
</template>

<style scoped>
.platforms-container { padding: 16px; }

.platform-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.platform-card {
  display: flex;
  align-items: center;
  padding: 14px;
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 12px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.platform-card:active { opacity: 0.7; }

.icon {
  font-size: 24px;
  margin-right: 16px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--tg-theme-bg-color);
  border-radius: 10px;
}

.info { flex-grow: 1; }

.name {
  font-weight: 600;
  color: var(--tg-theme-text-color);
}

.count {
  font-size: 13px;
  color: var(--tg-theme-hint-color);
}

.arrow {
  color: var(--tg-theme-hint-color);
  font-size: 20px;
}

.add-btn {
  margin-top: 20px;
  width: 100%;
  padding: 12px;
  border: 2px dashed var(--tg-theme-hint-color);
  background: none;
  color: var(--tg-theme-hint-color);
  border-radius: 12px;
  font-weight: 600;
}
</style>