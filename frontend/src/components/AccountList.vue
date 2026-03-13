<script setup>
import {ref, onMounted} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {accountApi} from '../api/account.js';

const emit = defineEmits(['select-account', 'add-account']);
const {tg, initData} = useTelegram();

const accounts = ref([]);
const isLoading = ref(true);
const error = ref(null);

const props = defineProps({
  platformId: String,
  platform: Object
});

onMounted(async () => {
  try {
    const response = await accountApi.getList(initData, props.platformId);
    accounts.value = response.data || response;
  } catch (e) {
    console.error("Ошибка загрузки:", e);
    error.value = "Не удалось загрузить аккаунты";
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <div class="accounts-container">
    <div class="platform-header">
      <div class="platform-info">
        <span class="platform-icon">{{ props.platform?.icon || '🌐' }}</span>
        <div class="platform-text">
          <h1>{{ props.platform?.name || 'Платформа' }}</h1>
          <p v-if="props.platform?.description" class="platform-desc">
            {{ props.platform.description }}
          </p>
        </div>
      </div>

      <button
          v-if="props.platform?.name !== 'Other'"
          class="edit-platform-btn"
          @click="$emit('edit-platform', props.platform)"
      >
        ✏️
      </button>
    </div>

    <div v-if="isLoading" class="status-msg">
      <div class="spinner"></div>
      <p>Загрузка данных...</p>
    </div>

    <div v-else-if="error" class="status-msg error">
      <p>{{ error }}</p>
    </div>

    <template v-else>
      <div class="accounts-list">

        <div v-if="accounts.length === 0" class="empty-state">
          <div class="empty-icon">📂</div>
          <p>В этой категории пока нет аккаунтов</p>
        </div>

        <div
            v-for="account in accounts"
            :key="account.id"
            class="account-item"
            @click="emit('select-account', account)"
        >
          <div class="icon-box">{{ platformIcon || '👤' }}</div>

          <div class="main-content">
            <div class="login-text">{{ account.login }}</div>
            <div v-if="account.label" class="label-text">{{ account.label }}</div>
          </div>

          <div class="chevron">›</div>
        </div>

        <div class="account-item add-button" @click="emit('add-account')">
          <div class="icon-box add-icon">+</div>
          <div class="main-content">
            <div class="name">Add New Account</div>
            <div class="description">Save credentials for this platform</div>
          </div>
        </div>

      </div>
    </template>
  </div>
</template>

<style scoped>
.accounts-container {
  width: 100%;
  padding: 16px 16px 50px;
  box-sizing: border-box;
}

.accounts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.account-item {
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  padding: 10px;
  gap: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.1s ease;
}

.account-item:active {
  transform: scale(0.98);
  opacity: 0.8;
}

.icon-box {
  width: 42px;
  height: 42px;
  min-width: 42px;
  background: var(--tg-theme-bg-color);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.main-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-text {
  font-weight: 600;
  font-size: 15px;
  color: var(--tg-theme-text-color);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.label-text {
  font-size: 11px;
  color: var(--tg-theme-hint-color);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chevron {
  color: var(--tg-theme-hint-color);
  font-size: 20px;
  opacity: 0.4;
}

/* Кнопка добавления */
.add-button {
  border: 1px dashed var(--tg-theme-button-color);
  background: transparent;
  margin-top: 8px;
}

.add-icon {
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  font-weight: bold;
}

.add-button .name {
  color: var(--tg-theme-button-color);
  font-weight: 600;
  font-size: 15px;
}

.add-button .description {
  font-size: 11px;
  color: var(--tg-theme-hint-color);
}

/* Вспомогательные стили */
.status-msg, .empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--tg-theme-hint-color);
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--tg-theme-hint-color);
  border-top-color: var(--tg-theme-button-color);
  border-radius: 50%;
  margin: 0 auto 12px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.platform-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  background: var(--tg-theme-bg-color);
  border-bottom: 2px solid rgba(128, 128, 128, 0.2);
  margin-bottom: 30px;
}

.platform-info {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.platform-icon {
  font-size: 32px;
  width: 52px;
  height: 52px;
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.platform-text h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--tg-theme-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.platform-desc {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: var(--tg-theme-hint-color);
  line-height: 1.3;
}

/* Кнопка редактирования платформы */
.edit-platform-btn {
  background: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.edit-platform-btn:active {
  opacity: 0.85;
  transform: scale(0.95);
}

</style>