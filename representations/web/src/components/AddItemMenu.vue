<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['add-account', 'add-category'])

const isOpen = ref(false)
const menuRef = ref(null)

const toggle = () => {
  isOpen.value = !isOpen.value
}

const chooseAccount = () => {
  isOpen.value = false
  emit('add-account')
}

const chooseCategory = () => {
  isOpen.value = false
  emit('add-category')
}

const onClickOutside = (event) => {
  if (menuRef.value && !menuRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div ref="menuRef" class="add-menu">
    <button
      class="icon-btn primary"
      title="Добавить"
      @click.stop="toggle"
    >＋</button>
    <div v-if="isOpen" class="add-menu-dropdown">
      <button class="add-menu-item" @click="chooseCategory">📁 Категория</button>
      <button class="add-menu-item" @click="chooseAccount">👤 Аккаунт</button>
    </div>
  </div>
</template>

<style scoped>
.add-menu {
  position: relative;
}

.add-menu-dropdown {
  position: absolute;
  top: calc(100% + 0.35rem);
  right: 0;
  min-width: 150px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-btn);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  overflow: hidden;
  z-index: 20;
}

.add-menu-item {
  display: block;
  width: 100%;
  padding: 0.65rem 0.85rem;
  background: none;
  border: none;
  border-bottom: 1px solid var(--color-separator);
  color: var(--color-text);
  font-size: 0.9rem;
  text-align: left;
  cursor: pointer;
}

.add-menu-item:last-child {
  border-bottom: none;
}

.add-menu-item:hover {
  background: var(--color-hover);
}
</style>
