const tg = () => window.Telegram?.WebApp ?? null

/** Telegram отдаёт результат колбэком — приводим к промису, как в общем интерфейсе. */
export const tgPlatform = {
    alert(message) {
        return new Promise((resolve) => {
            const api = tg()
            if (!api?.showAlert) {
                window.alert(message)
                resolve()
                return
            }
            api.showAlert(message, () => resolve())
        })
    },

    confirm(message) {
        return new Promise((resolve) => {
            const api = tg()
            if (!api?.showConfirm) {
                resolve(window.confirm(message))
                return
            }
            api.showConfirm(message, (confirmed) => resolve(!!confirmed))
        })
    },

    haptic(kind = 'light') {
        const haptics = tg()?.HapticFeedback
        if (!haptics) return
        try {
            if (['success', 'warning', 'error'].includes(kind)) {
                haptics.notificationOccurred(kind)
            } else {
                haptics.impactOccurred(kind)
            }
        } catch {
            // тактильная отдача — необязательная мелочь, молчим
        }
    },
}
