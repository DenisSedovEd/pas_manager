/**
 * Копирование с деградацией: Clipboard API → Telegram → execCommand.
 * Каскад нужен потому, что внутри Telegram-вебвью navigator.clipboard
 * доступен не всегда, а на старых iOS не работает и он.
 */
export async function writeClipboard(text) {
    if (!text) return false

    try {
        if (navigator.clipboard?.writeText) {
            await navigator.clipboard.writeText(text)
            return true
        }
    } catch {
        // нет разрешения или не защищённый контекст — пробуем дальше
    }

    try {
        const tg = window.Telegram?.WebApp
        if (tg?.writeTextToClipboard) {
            await tg.writeTextToClipboard(text)
            return true
        }
    } catch {
        // не в Telegram или метод недоступен
    }

    const el = document.createElement('textarea')
    el.value = text
    el.setAttribute('readonly', '')
    el.style.position = 'fixed'
    el.style.opacity = '0'
    el.style.left = '-9999px'
    document.body.appendChild(el)
    el.focus()
    el.select()

    let success = false
    try {
        success = document.execCommand('copy')
    } catch {
        success = false
    }

    document.body.removeChild(el)
    return success
}
