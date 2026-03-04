<script setup>
import { ref, onMounted } from 'vue';
import { useTelegram } from '../composables/useTelegram';

const props = defineProps(['platformId']);
const emit = defineEmits(['select-account']); // Объявляем событие
const { initData } = useTelegram();
const accounts = ref([]);

onMounted(async () => {
  try {
    const res = await fetch(`/pas-manager/v1/account/list/${props.platformId}`, {
      headers: { 'Authorization': initData }
    });
    accounts.value = await res.json();
  } catch (e) {
    console.error("Ошибка загрузки аккаунтов:", e);
  }
});
</script>

<template>
  <div class="account-list">
    <div
      v-for="acc in accounts"
      :key="acc.id"
      class="account-card"
      @click="emit('select-account', acc)"
    >
      <div class="acc-info">
        <span class="label">{{ acc.label }}</span>
        <span class="login">{{ acc.login }}</span>
      </div>
      <div class="arrow">›</div>
    </div>
  </div>
</template>

<style scoped>
.account-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  box-sizing: border-box; /* Важно для десктопа */
}

.account-card {
  background: var(--tg-theme-secondary-bg-color);
  padding: 15px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%; /* Растягиваем */
  box-sizing: border-box;
}

.account-card:active {
  opacity: 0.7; /* Визуальный отклик при нажатии */
}

.acc-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1; /* Занимает всё пространство до стрелочки */
  min-width: 0;
}
.label {
  font-size: 12px;
  color: var(--tg-theme-hint-color);
}

.login {
  font-weight: bold;
  color: var(--tg-theme-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.arrow {
  color: var(--tg-theme-hint-color);
  font-size: 20px;
  font-weight: bold;
}
</style>