<script setup>
import ConfirmDialog from './ConfirmDialog.vue'

const props = defineProps({
    host: { type: Object, required: true },
})
</script>

<template>
  <ConfirmDialog
    v-for="dialog in props.host.dialogs.value"
    :key="dialog.id"
    :kind="dialog.kind"
    :title="dialog.title || ''"
    :message="dialog.message || ''"
    :confirm-text="dialog.confirmText || (dialog.kind === 'alert' ? 'Понятно' : 'Да')"
    :cancel-text="dialog.cancelText || 'Отмена'"
    :danger="!!dialog.danger"
    @confirm="props.host.settle(dialog.id, true)"
    @cancel="props.host.settle(dialog.id, false)"
  />
</template>
