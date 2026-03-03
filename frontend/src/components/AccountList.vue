<script setup>
import { ref, onMounted } from 'vue';
import { useTelegram } from '../composables/useTelegram';

const props = defineProps(['platformId']);
const { tg, initData } = useTelegram();
const accounts = ref([]);

onMounted(async () => {
  // Запрос к нашей новой ручке
  const res = await fetch(`/pas-manager/v1/account/list/${props.platformId}`, {
    headers: { 'Authorization': initData }
  });
  accounts.value = await res.json();
});

const copyPassword = (accountId) => {
  // Пока это заглушка, просто уведомление
  tg.HapticFeedback.notificationOccurred('success');
  tg.showAlert(`Пароль для аккаунта ${accountId} скопирован!`);
};
</script>

<template>
  <div class="account-list">
    <div v-for="acc in accounts" :key="acc.id" class="account-card">
      <div class="acc-info">
        <span class="label">{{ acc.label }}</span>
        <span class="login">{{ acc.login }}</span>
      </div>
      <button @click="copyPassword(acc.id)" class="copy-btn">🔑 Копировать</button>
    </div>
  </div>
</template>

<style scoped>
.account-list { padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.account-card {
  background: var(--tg-theme-secondary-bg-color);
  padding: 15px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.acc-info { display: flex; flex-direction: column; }
.label { font-size: 12px; color: var(--tg-theme-hint-color); }
.login { font-weight: bold; }
.copy-btn {
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  border: none;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
}
.back-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--tg-theme-button-color);
  cursor: pointer;
}
</style>