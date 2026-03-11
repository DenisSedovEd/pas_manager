<script setup>
import {useRouter} from 'vue-router';

const router = useRouter();
</script>

<template>
  <div class="page p-16">
    <div class="menu-list">
      <button class="menu-card" @click="router.push('/platforms')">
        <span class="icon">💼</span>
        <div class="text">
          <b>Платформы</b>
          <p>Ваши аккаунты и доступы</p>
        </div>
      </button>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 16px;
}

.menu-card {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  border-radius: 16px;
  background: var(--tg-theme-secondary-bg-color);
  border: 1px solid rgba(0, 0, 0, 0.05);
  text-align: left;
  color: inherit;
  margin-bottom: 12px;
}

.icon {
  font-size: 32px;
}

b {
  display: block;
  font-size: 18px;
}

p {
  margin: 4px 0 0;
  font-size: 13px;
  opacity: 0.6;
}
</style>