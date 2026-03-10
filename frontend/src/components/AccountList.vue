<script setup>
import { ref, onMounted } from 'vue';
import { useTelegram } from '../composables/useTelegram';

const props = defineProps(['platformId']);
const emit = defineEmits(['select-account', 'add-account']);
const { initData } = useTelegram();
const accounts = ref([]);
const isLoading = ref(true);

onMounted(async () => {
  try {
    const res = await fetch(`/pas-manager/v1/account/list/${props.platformId}`, {
      headers: { 'Authorization': initData }
    });
    accounts.value = await res.json();
  } catch (e) {
    console.error("Ошибка загрузки аккаунтов:", e);
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div class="account-list-container">
    <div v-if="isLoading" class="loader">Загрузка аккаунтов...</div>

    <template v-else>
      <div class="account-grid">
        <div
          v-for="acc in accounts"
          :key="acc.id"
          class="account-card"
          @click="emit('select-account', acc)"
        >
          <div class="account-content">
            <div class="label">{{ acc.label }}</div>
            <div class="login">{{ acc.login }}</div>
          </div>
        </div>
      </div>

      <button class="add-btn" @click="emit('add-account')">+ Добавить аккаунт</button>
    </template>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.account-list-container {
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

.account-grid {
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

.account-card {
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 12px;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: transform 0.1s ease;
}

.account-card:active {
  transform: scale(0.95);
}

.account-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  text-align: center;
}

.label {
  font-size: 11px;
  color: var(--tg-theme-hint-color);
  font-weight: 500;
}

.login {
  font-weight: 600;
  font-size: 13px;
  color: var(--tg-theme-text-color);
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
  font-size: 14px;
  cursor: pointer;
  margin: 16px;
  width: calc(100% - 32px);
  transition: opacity 0.2s;
}

.add-btn:active {
  opacity: 0.7;
}
</style>