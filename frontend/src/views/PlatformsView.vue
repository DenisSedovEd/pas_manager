<script setup>
import {ref, onMounted} from 'vue';
import {useRouter} from 'vue-router';
import {platformApi} from '../api/platform.js';
import {useTelegram} from '../composables/useTelegram';

const router = useRouter();
const {tg, initData} = useTelegram();
const platforms = ref([]);
const isLoading = ref(true);

onMounted(async () => {
  try {
    const res = await platformApi.getList(initData);
    platforms.value = res.data || res;
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div class="page scrollable p-16">
    <div class="header">
      <h2>Платформы</h2>
      <button class="add-fab" @click="router.push('/platforms/new')">+</button>
    </div>
    <div v-if="isLoading" class="loader">Загрузка...</div>
    <div v-else class="grid">
      <div v-for="p in platforms" :key="p.id" class="p-card" @click="router.push(`/platforms/${p.id}/accounts`)">
        <div class="p-icon">{{ p.icon || '🌐' }}</div>
        <div class="p-name">{{ p.name }}</div>
        <div class="p-count">{{ p.accounts_count }} аккаунтов</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scrollable {
  overflow-y: auto;
  height: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.p-card {
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
}

.p-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.p-count {
  font-size: 11px;
  opacity: 0.5;
}

.add-fab {
  width: 44px;
  height: 44px;
  border-radius: 22px;
  background: var(--tg-theme-button-color);
  color: white;
  border: none;
  font-size: 24px;
}
</style>