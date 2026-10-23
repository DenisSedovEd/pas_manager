import { ref } from 'vue'

let seq = 0

/**
 * Очередь диалогов для представлений без системных окон (web).
 * Каждый вызов возвращает промис, который разрешается выбором пользователя.
 */
export function createDialogHost() {
    const dialogs = ref([])

    const push = (dialog) =>
        new Promise((resolve) => {
            dialogs.value.push({ ...dialog, id: ++seq, resolve })
        })

    const settle = (id, value) => {
        const index = dialogs.value.findIndex((d) => d.id === id)
        if (index === -1) return
        const [dialog] = dialogs.value.splice(index, 1)
        dialog.resolve(value)
    }

    return {
        dialogs,
        settle,
        alert: (message, options = {}) => push({ kind: 'alert', message, ...options }),
        confirm: (message, options = {}) => push({ kind: 'confirm', message, ...options }),
        haptic: () => {},
    }
}
