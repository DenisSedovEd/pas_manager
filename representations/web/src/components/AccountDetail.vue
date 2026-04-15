<script setup>
import { ref, computed, onMounted } from 'vue'
import { accountApi } from '../api/account.js'

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
      <button class="sub-back-btn" @click="$emit('go-back')">←</button>
      <button v-if="fullAccount" class="icon-btn primary" @click="$emit('edit', fullAccount)">Изменить</button>
    </div>

    <div v-if="isLoading" class="loading">Загрузка...</div>

    <template v-else-if="fullAccount">
      <div class="header-section">
        <div class="account-avatar">{{ props.category?.icon || '👤' }}</div>
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
.screen { padding: 0; }
.screen-header {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 1rem 1rem 0.5rem;
  border-bottom: 1px solid #2c313c;
}
.sub-back-btn {
  position: absolute;
  left: 1rem;
  border: none;
  background: none;
  color: #61afef;
  font-size: 1.25rem;
  cursor: pointer;
}
.screen-header h2 { margin: 0; font-size: 1.25rem; }
.icon-btn.primary {
  position: absolute;
  right: 1rem;
  background: #61afef;
  color: #1e2127;
  border: none;
  border-radius: 8px;
  padding: 0.4rem 0.9rem;
  cursor: pointer;
  font-size: 0.9rem;
}
.header-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.25rem 1rem 0.75rem;
  border-bottom: 1px solid #2c313c;
}
.account-avatar {
  font-size: 44px;
  width: 80px;
  height: 80px;
  background: #2c313c;
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #abb2bf;
  margin-bottom: 12px;
}
.account-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 4px;
  text-align: center;
  color: #e6c07b;
}
.category-tag { font-weight: 400; color: #8fbcbb; font-size: 0.95rem; }
.account-subtitle { color: #8f919d; margin: 0; font-size: 0.95rem; text-align: center; }
.loading { padding: 2rem; text-align: center; color: #8f919d; }
.info-cards { padding: 1rem; display: flex; flex-direction: column; gap: 0.75rem; }
.info-card {
  display: flex;
  align-items: center;
  background: #2c313c;
  border-radius: 12px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  gap: 0.75rem;
  transition: background 0.15s;
}
.info-card:hover { background: #2f343f; }
.card-content { flex: 1; display: flex; flex-direction: column; gap: 2px; }
label { font-size: 0.75rem; color: #8f919d; text-transform: uppercase; }
.value { font-size: 1rem; font-weight: 500; word-break: break-all; color: #dcdfe4; }
.copy-icon { font-size: 1.1rem; flex-shrink: 0; color: #61afef; }
.copy-icon.copied { opacity: 0.6; }
.password-card { align-items: center; }
.card-actions { display: flex; gap: 0.5rem; align-items: center; }
.toggle-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0;
  color: #61afef;
}
</style>
