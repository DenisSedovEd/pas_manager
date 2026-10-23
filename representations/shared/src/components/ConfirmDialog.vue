<script setup>
import { onMounted, onUnmounted } from 'vue'

const props = defineProps({
    kind: { type: String, default: 'confirm' }, // 'confirm' | 'alert'
    title: { type: String, default: '' },
    message: { type: String, default: '' },
    confirmText: { type: String, default: 'Да' },
    cancelText: { type: String, default: 'Отмена' },
    danger: { type: Boolean, default: false },
})

const emit = defineEmits(['confirm', 'cancel'])

const dismiss = () => emit(props.kind === 'alert' ? 'confirm' : 'cancel')

const onKeydown = (event) => {
    if (event.key === 'Escape') dismiss()
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div class="pas-dialog-backdrop" @click.self="dismiss">
    <div class="pas-dialog-card" role="alertdialog" :aria-label="title || message">
      <h3 v-if="title" class="pas-dialog-title">{{ title }}</h3>
      <p v-if="message" class="pas-dialog-message">{{ message }}</p>
      <div class="pas-dialog-actions">
        <button
          type="button"
          class="pas-dialog-btn pas-dialog-btn--primary"
          :class="{ 'pas-dialog-btn--danger': danger }"
          @click="$emit('confirm')"
        >{{ confirmText }}</button>
        <button
          v-if="kind !== 'alert'"
          type="button"
          class="pas-dialog-btn pas-dialog-btn--secondary"
          @click="$emit('cancel')"
        >{{ cancelText }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/*
 * Цвета приходят из приложения через --pas-dialog-*: у web своя палитра,
 * у mini app — переменные темы Telegram. Запасные значения на случай,
 * если слой темы ещё не подключён.
 */
.pas-dialog-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 1100;
}

.pas-dialog-card {
  width: min(100%, 400px);
  background: var(--pas-dialog-surface, #21252b);
  border: 1px solid var(--pas-dialog-border, rgba(128, 128, 128, 0.25));
  border-radius: 14px;
  padding: 1.25rem;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
}

.pas-dialog-title {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: var(--pas-dialog-text, #abb2bf);
}

.pas-dialog-message {
  margin: 0 0 1rem;
  line-height: 1.45;
  color: var(--pas-dialog-muted, #8f919d);
  white-space: pre-line;
}

.pas-dialog-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pas-dialog-btn {
  width: 100%;
  padding: 0.75rem;
  border-radius: 10px;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  font-family: inherit;
}

.pas-dialog-btn--primary {
  background: var(--pas-dialog-accent, #61afef);
  color: var(--pas-dialog-accent-text, #fff);
}

.pas-dialog-btn--danger {
  background: var(--pas-dialog-danger, #ff3b30);
  color: #fff;
}

.pas-dialog-btn--secondary {
  background: transparent;
  color: var(--pas-dialog-muted, #8f919d);
  border: 1.5px solid var(--pas-dialog-border, rgba(128, 128, 128, 0.25));
}
</style>
