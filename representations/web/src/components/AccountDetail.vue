<script setup>
import { ref, computed, onMounted } from 'vue'
import { accountApi } from '../api/account.js'
import CategoryIcon from './CategoryIcon.vue'

const props = defineProps(['account', 'resources', 'category'])
const emit = defineEmits(['edit', 'deleted', 'go-back'])

const fullAccount = ref(null)
const isLoading = ref(true)
const showPassword = ref(false)
const copyStatus = ref({})

const resourceName = computed(() => {
  const rid = fullAccount.value?.resource_id || props.account?.resource_id
  return props.resources?.find(r => r.id === rid)?.resource_name || '-'
})

const copyToClipboard = async (text, field) => {
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
    copyStatus.value[field] = true
    setTimeout(() => { copyStatus.value[field] = false }, 2000)
  } catch {
    alert('Не удалось скопировать в буфер обмена')
  }
}

onMounted(async () => {
  try {
    fullAccount.value = await accountApi.getDetail(props.account.id)
  } catch {
    alert('Не удалось загрузить данные аккаунта')
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="screen">
    <div class="screen-header">
      <button class="sub-back-btn" @click="$emit('go-back')">⬅️</button>
      <button v-if="fullAccount" class="icon-btn" title="Редактировать" @click="$emit('edit', fullAccount)">✏️</button>
    </div>

    <div v-if="isLoading" class="loading">Загрузка...</div>

    <template v-else-if="fullAccount">
      <div class="header-section">
        <div class="account-avatar"><CategoryIcon :icon="props.category?.icon" fallback="👤" size="xl" /></div>
        <h2 class="account-title">
          {{ resourceName }}
          <span v-if="props.category?.name" class="category-tag"> ({{ props.category.name }})</span>
        </h2>
        <p class="account-subtitle">{{ fullAccount.label || fullAccount.login }}</p>
      </div>

      <div class="info-cards">
        <div class="info-card" @click="copyToClipboard(fullAccount.login, 'login')">
          <div class="card-content">
            <label>Логин</label>
            <div class="value">{{ fullAccount.login }}</div>
          </div>
          <span class="copy-icon" :class="{ copied: copyStatus['login'] }">
            {{ copyStatus['login'] ? '✅' : '📋' }}
          </span>
        </div>

        <div class="info-card password-card">
          <div class="card-content" @click="copyToClipboard(fullAccount.password, 'pass')">
            <label>Пароль</label>
            <div class="value">{{ showPassword ? fullAccount.password : '••••••••••' }}</div>
          </div>
          <div class="card-actions">
            <button class="toggle-btn" @click.stop="showPassword = !showPassword">
              {{ showPassword ? '🔓' : '🔒' }}
            </button>
            <span class="copy-icon" @click.stop="copyToClipboard(fullAccount.password, 'pass')" :class="{ copied: copyStatus['pass'] }">
              {{ copyStatus['pass'] ? '✅' : '📋' }}
            </span>
          </div>
        </div>

        <div v-if="fullAccount.email" class="info-card" @click="copyToClipboard(fullAccount.email, 'email')">
          <div class="card-content">
            <label>E-mail</label>
            <div class="value">{{ fullAccount.email }}</div>
          </div>
          <span class="copy-icon" :class="{ copied: copyStatus['email'] }">
            {{ copyStatus['email'] ? '✅' : '📋' }}
          </span>
        </div>

        <div v-if="fullAccount.phone" class="info-card" @click="copyToClipboard(fullAccount.phone, 'phone')">
          <div class="card-content">
            <label>Телефон</label>
            <div class="value">{{ fullAccount.phone }}</div>
          </div>
          <span class="copy-icon" :class="{ copied: copyStatus['phone'] }">
            {{ copyStatus['phone'] ? '✅' : '📋' }}
          </span>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* Убираем border-bottom глобального screen-header — тут его нет */
.screen-header {
  padding: 0.875rem 1rem 0.75rem;
  border-bottom: none;
  gap: 0.75rem;
}

/* Квадратная иконка-кнопка (переопределяет глобальный .icon-btn) */
.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  padding: 0;
  font-size: 1.1rem;
  flex-shrink: 0;
  border-radius: 10px;
}

.header-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.25rem 1rem 0.75rem;
  border-bottom: 1px solid var(--color-separator);
}

.account-avatar {
  font-size: 44px;
  width: 80px;
  height: 80px;
  background: var(--color-hover);
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text);
  margin-bottom: 12px;
}

.account-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 4px;
  text-align: center;
  color: var(--color-title);
}

.category-tag { font-weight: 400; color: var(--color-teal); font-size: 0.95rem; }
.account-subtitle { color: var(--color-hint); margin: 0; font-size: 0.95rem; text-align: center; }

.info-cards { padding: 1rem; display: flex; flex-direction: column; gap: 0.75rem; }

.info-card {
  display: flex;
  align-items: center;
  background: var(--color-hover);
  border-radius: var(--radius-card);
  padding: 0.75rem 1rem;
  cursor: pointer;
  gap: 0.75rem;
  transition: background 0.15s;
}

.info-card:hover { background: #2f343f; }
.card-content { flex: 1; display: flex; flex-direction: column; gap: 2px; }
label { font-size: 0.75rem; color: var(--color-hint); text-transform: uppercase; }
.value { font-size: 1rem; font-weight: 500; word-break: break-all; color: #dcdfe4; }
.copy-icon { font-size: 1.1rem; flex-shrink: 0; color: var(--color-accent); }
.copy-icon.copied { opacity: 0.6; }
.password-card { align-items: center; }
.card-actions { display: flex; gap: 0.5rem; align-items: center; }
.toggle-btn { background: none; border: none; font-size: 1.1rem; cursor: pointer; padding: 0; color: var(--color-accent); }
</style>
