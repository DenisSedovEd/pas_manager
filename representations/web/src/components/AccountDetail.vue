<script setup>
import { ref, computed, onMounted } from 'vue'
import { accountApi } from '../api/account.js'

const props = defineProps(['account', 'resources', 'category'])
const emit = defineEmits(['edit', 'deleted'])

const fullAccount = ref(null)
const isLoading = ref(true)
const showPassword = ref(false)
const copyStatus = ref({})

const resourceName = computed(() => {
  const rid = fullAccount.value?.resource_id || props.account?.resource_id
  return props.resources?.find(r => r.id === rid)?.resource_name || 'Без площадки'
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
      <h2>{{ resourceName }}</h2>
      <button v-if="fullAccount" class="icon-btn primary" @click="$emit('edit', fullAccount)">Изменить</button>
    </div>

    <div v-if="isLoading" class="loading">Загрузка...</div>

    <template v-else-if="fullAccount">
      <p class="account-subtitle">{{ fullAccount.label || fullAccount.login }}</p>

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
  justify-content: space-between;
  padding: 1rem 1rem 0.5rem;
  border-bottom: 1px solid #eee;
}
.screen-header h2 { margin: 0; font-size: 1.25rem; }
.icon-btn.primary {
  background: #5856d6;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.4rem 0.9rem;
  cursor: pointer;
  font-size: 0.9rem;
}
.account-subtitle { padding: 0.25rem 1rem 0; color: #666; margin: 0; font-size: 0.95rem; }
.loading { padding: 2rem; text-align: center; color: #999; }
.info-cards { padding: 1rem; display: flex; flex-direction: column; gap: 0.75rem; }
.info-card {
  display: flex;
  align-items: center;
  background: #f8f8fa;
  border-radius: 12px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  gap: 0.75rem;
  transition: background 0.15s;
}
.info-card:hover { background: #efeffa; }
.card-content { flex: 1; display: flex; flex-direction: column; gap: 2px; }
label { font-size: 0.75rem; color: #888; text-transform: uppercase; }
.value { font-size: 1rem; font-weight: 500; word-break: break-all; }
.copy-icon { font-size: 1.1rem; flex-shrink: 0; }
.copy-icon.copied { opacity: 0.6; }
.password-card { align-items: center; }
.card-actions { display: flex; gap: 0.5rem; align-items: center; }
.toggle-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0;
}
</style>
