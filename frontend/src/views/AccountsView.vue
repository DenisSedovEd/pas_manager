<script setup>
import {ref, onMounted} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {accountApi} from '../api/account.js';
import {useTelegram} from '../composables/useTelegram';

const route = useRoute();
const router = useRouter();
const {initData} = useTelegram();
const accounts = ref([]);
const platformId = route.params.platformId;

onMounted(async () => {
  accounts.value = await accountApi.getList(initData, platformId);
});
</script>

<template>
  <div class="page scrollable p-16">
    <div class="header">
      <h3>Аккаунты</h3>
      <button class="add-fab" @click="router.push(`/accounts/new/${platformId}`)">+</button>
    </div>
    <div class="acc-list">
      <div v-for="acc in accounts" :key="acc.id" class="acc-item" @click="router.push(`/accounts/${acc.id}`)">
        <div class="acc-info">
          <span class="acc-login">{{ acc.login }}</span>
          <span class="acc-label">{{ acc.label }}</span>
        </div>
        <span class="chevron">›</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.acc-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.acc-item {
  background: var(--tg-theme-secondary-bg-color);
  padding: 14px 16px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.acc-info {
  display: flex;
  flex-direction: column;
}

.acc-label {
  font-size: 11px;
  opacity: 0.5;
}

.chevron {
  color: gray;
  font-size: 20px;
}
</style>