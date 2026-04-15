<script setup>
import { ref } from 'vue'
import { useWebAuth } from '../composables/useWebAuth.js'

const emit = defineEmits(['authenticated'])
const { login } = useWebAuth()

const password = ref('')
const error = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  if (!password.value || isLoading.value) return
  isLoading.value = true
  error.value = ''
  try {
    await login(password.value)
    emit('authenticated')
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="login-screen">
    <div class="login-card">
      <div class="login-icon">🔐</div>
      <h1>Safe Manager</h1>
      <p class="subtitle">Введи мастер-пароль для входа</p>

      <form @submit.prevent="handleSubmit" class="login-form">
        <input
          v-model="password"
          type="password"
          placeholder="Мастер-пароль"
          autocomplete="current-password"
          autofocus
          :disabled="isLoading"
        />
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" :disabled="isLoading || !password">
          {{ isLoading ? 'Проверка...' : 'Войти' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f4f4f8;
}
.login-card {
  background: white;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  width: 100%;
  max-width: 360px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  text-align: center;
}
.login-icon { font-size: 3rem; margin-bottom: 0.5rem; }
h1 { margin: 0 0 0.25rem; font-size: 1.5rem; }
.subtitle { color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }
.login-form { display: flex; flex-direction: column; gap: 0.75rem; }
input {
  padding: 0.75rem 1rem;
  border: 1.5px solid #ddd;
  border-radius: 10px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
}
input:focus { border-color: #5856d6; }
button {
  padding: 0.75rem;
  background: #5856d6;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  cursor: pointer;
  transition: opacity 0.2s;
}
button:disabled { opacity: 0.5; cursor: default; }
.error-msg { color: #ff3b30; font-size: 0.85rem; margin: 0; }
</style>
