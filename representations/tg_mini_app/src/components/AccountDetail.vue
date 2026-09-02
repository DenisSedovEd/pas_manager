<script setup>
import {ref, computed, onMounted, onUnmounted} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {accountApi} from '../api/account.js';
import CategoryIcon from './CategoryIcon.vue';

const props = defineProps(['account', 'resources', 'category']);
const emit = defineEmits(['edit', 'deleted']);

const {tg, initData} = useTelegram();

const fullAccount = ref(null);

const resourceName = computed(() => {
  const resourceId = fullAccount.value?.resource_id || props.account?.resource_id;
  if (!props.resources?.length || !resourceId) return 'Без площадки';
  return props.resources.find(r => r.id === resourceId)?.resource_name || 'Без площадки';
});

const categoryName = computed(() => {
  return props.category?.name || props.category?.category_name || '';
});
const isLoading = ref(true);
const showPassword = ref(false);
const copyStatus = ref({});

onMounted(async () => {
  try {
    fullAccount.value = await accountApi.getDetail(initData, props.account.id);
  } catch (error) {
    tg.showAlert("Не удалось загрузить данные");
  } finally {
    isLoading.value = false;
  }

  tg.MainButton.setText('Изменить данные');
  tg.MainButton.onClick(onEditClick);
  tg.MainButton.show();
});

onUnmounted(() => {
  tg.MainButton.hide();
  tg.MainButton.offClick(onEditClick);
});

const onEditClick = () => {
  if (fullAccount.value) emit('edit', fullAccount.value);
};

const copyToClipboard = async (text, field) => {
  if (!text) return;

  const writeText = async (value) => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value);
        return true;
      }
    } catch {}

    try {
      if (tg?.writeTextToClipboard) {
        await tg.writeTextToClipboard(value);
        return true;
      }
    } catch {}

    const el = document.createElement('textarea');
    el.value = value;
    el.setAttribute('readonly', '');
    el.style.position = 'fixed';
    el.style.opacity = '0';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.focus();
    el.select();

    let success = false;
    try {
      success = document.execCommand('copy');
    } catch {}

    document.body.removeChild(el);
    return success;
  };

  const copied = await writeText(text);
  if (!copied) {
    tg?.showAlert?.('Не удалось скопировать в буфер обмена');
    return;
  }

  tg.HapticFeedback.notificationOccurred('success');
  copyStatus.value[field] = true;
  setTimeout(() => {
    copyStatus.value[field] = false;
  }, 2000);
};
</script>

<template>
  <div class="detail-container">
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
    </div>

    <template v-else-if="fullAccount">
      <div class="header-section">
        <div class="account-avatar">
          <CategoryIcon :icon="props.category?.icon" fallback="👤" size="xl" />
        </div>
        <h2 class="account-title">{{ resourceName }}<span v-if="categoryName" class="category-tag"> ({{ categoryName }})</span></h2>
        <p class="account-subtitle">{{ fullAccount.label || fullAccount.login }}</p>
      </div>

      <div class="info-cards">

        <div class="info-card" @click="copyToClipboard(fullAccount.login, 'login')">
          <div class="card-content">
            <label>Логин</label>
            <div class="value">{{ fullAccount.login }}</div>
          </div>
          <div class="copy-icon" :class="{ 'copied': copyStatus['login'] }">
            {{ copyStatus['login'] ? '✅' : '📋' }}
          </div>
        </div>

        <div class="info-card password-card">
          <div class="card-content" @click="copyToClipboard(fullAccount.password, 'pass')">
            <label>Пароль</label>
            <div class="value">
              {{ showPassword ? fullAccount.password : '••••••••••••' }}
            </div>
          </div>
          <div class="card-actions">
            <button class="toggle-btn" @click="showPassword = !showPassword">
              {{ showPassword ? '🔓' : '🔒' }}
            </button>
            <div class="copy-icon" @click="copyToClipboard(fullAccount.password, 'pass')"
                 :class="{ 'copied': copyStatus['pass'] }">
              {{ copyStatus['pass'] ? '✅' : '📋' }}
            </div>
          </div>
        </div>

        <div v-if="fullAccount.email" class="info-card" @click="copyToClipboard(fullAccount.email, 'email')">
          <div class="card-content">
            <label>E-mail</label>
            <div class="value">{{ fullAccount.email }}</div>
          </div>
          <div class="copy-icon" :class="{ 'copied': copyStatus['email'] }">
            {{ copyStatus['email'] ? '✅' : '📋' }}
          </div>
        </div>

        <div v-if="fullAccount.phone" class="info-card" @click="copyToClipboard(fullAccount.phone, 'phone')">
          <div class="card-content">
            <label>Телефон</label>
            <div class="value">{{ fullAccount.phone }}</div>
          </div>
          <div class="copy-icon" :class="{ 'copied': copyStatus['phone'] }">
            {{ copyStatus['phone'] ? '✅' : '📋' }}
          </div>
        </div>

      </div>
    </template>
  </div>
</template>

<style scoped>
.detail-container {
  padding: 16px;
  padding-bottom: 20px;
}

.header-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}

.account-avatar {
  font-size: 44px;
  width: 80px;
  height: 80px;
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(128, 128, 128, 0.1);
  margin-bottom: 12px;
}

.account-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--tg-theme-text-color);
}

.category-tag {
  font-size: 14px;
  font-weight: 400;
  color: var(--tg-theme-hint-color);
}

.account-subtitle {
  font-size: 13px;
  color: var(--tg-theme-hint-color);
  margin-top: 4px;
}

.info-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-card {
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 14px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: background 0.2s;
}

.info-card:active {
  background: rgba(128, 128, 128, 0.1);
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-content label {
  display: block;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--tg-theme-hint-color);
  margin-bottom: 4px;
}

.value {
  font-size: 16px;
  font-weight: 500;
  color: var(--tg-theme-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: 'SF Mono', 'Roboto Mono', monospace;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toggle-btn {
  background: none;
  border: none;
  font-size: 20px;
  padding: 0;
  cursor: pointer;
}

.copy-icon {
  font-size: 18px;
  opacity: 0.5;
  transition: all 0.2s;
}

.copy-icon.copied {
  opacity: 1;
  transform: scale(1.2);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 50px;
}
</style>