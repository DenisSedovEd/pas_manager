<script setup>
import {ref, onMounted} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {accountApi} from '../api/account.js';

const props = defineProps(['platformId']);
const emit = defineEmits(['select-account', 'add-account']);
const {tg, initData} = useTelegram();
const accounts = ref([]);
const isLoading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    // Получаем только аккаунты, инфа о платформе уже в App.vue
    accounts.value = await accountApi.getList(initData, props.platformId);
  } catch (e) {
    console.error("Ошибка загрузки:", e);
    error.value = "Не удалось загрузить";
    tg.showAlert("Ошибка загрузки");
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div class="accounts-container">
    <div v-if="isLoading" class="loader">Загрузка аккаунтов...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else>
      <div v-if="accounts.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">Нет аккаунтов</div>
      </div>

      <div v-else class="accounts-list">
        <div
            v-for="account in accounts"
            :key="account.id"
            class="account-card"
            @click="emit('select-account', account)"
        >
          <div class="account-content">
            <div class="login">{{ account.label }}</div>
            <div class="label">{{ account.login }}</div>
          </div>
          <div class="arrow">→</div>
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

.accounts-container {
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 12px;
  color: var(--tg-theme-hint-color);
}

.empty-icon {
  font-size: 48px;
}

.empty-text {
  font-size: 14px;
}

.accounts-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.account-card {
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: transform 0.1s ease;
}

.account-card:active {
  transform: scale(0.98);
}

.account-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.login {
  font-weight: 600;
  font-size: 14px;
  color: var(--tg-theme-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.label {
  font-size: 11px;
  color: var(--tg-theme-hint-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.arrow {
  color: var(--tg-theme-hint-color);
  font-size: 16px;
  margin-left: 8px;
  flex-shrink: 0;
}

.add-btn {
  flex-shrink: 0;
  background: var(--tg-theme-secondary-bg-color);
  border: 2px dashed var(--tg-theme-hint-color);
  color: var(--tg-theme-hint-color);
  padding: 12px;
  border-radius: 12px;
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