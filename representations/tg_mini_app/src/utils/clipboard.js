export function initTelegramClipboard() {

  const tg = window.Telegram?.WebApp
  let lastFocused = null

  const isEditable = (el) => {
    if (!el) return false

    return (
      el.tagName === "INPUT" ||
      el.tagName === "TEXTAREA" ||
      el.isContentEditable
    )
  }

  const isTouchDevice = () => (
    'ontouchstart' in window || navigator.maxTouchPoints > 0
  )

  document.addEventListener('contextmenu', (e) => {
    if (!isEditable(e.target)) {
      e.preventDefault()
    }
  })

  document.addEventListener('selectstart', (e) => {
    if (!isEditable(e.target)) {
      e.preventDefault()
    }
  })

  document.addEventListener('touchend', () => {
    if (isEditable(document.activeElement)) return
    window.getSelection()?.removeAllRanges()
  }, { passive: true })

  const getSelectedText = (target) => {

    if (!target) return ""

    if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") {
      return target.value.substring(
        target.selectionStart,
        target.selectionEnd
      )
    }

    return window.getSelection()?.toString() || ""
  }

  const insertText = (target, text) => {

    if (!target || !text) return

    if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") {

      const start = target.selectionStart ?? 0
      const end = target.selectionEnd ?? 0

      const value = target.value

      target.value =
        value.slice(0, start) +
        text +
        value.slice(end)

      const cursor = start + text.length

      target.setSelectionRange(cursor, cursor)

      target.dispatchEvent(new Event("input", { bubbles: true }))

      return
    }

    if (target.isContentEditable) {
      document.execCommand("insertText", false, text)
    }
  }

  const readClipboard = async () => {

    try {
      if (navigator.clipboard?.readText) {
        const text = await navigator.clipboard.readText()
        if (text) return text
      }
    } catch { }

    return new Promise((resolve) => {

      if (tg?.readTextFromClipboard) {

        tg.readTextFromClipboard((text) => {
          resolve(text || "")
        })

      } else {
        resolve("")
      }

    })
  }

  const writeClipboard = async (text) => {

    if (!text) return false

    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text)
        return true
      }
    } catch { }

    try {
      if (tg?.writeTextToClipboard) {
        await tg.writeTextToClipboard(text)
        return true
      }
    } catch { }

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
    } catch { }

    document.body.removeChild(el)
    return success
  }

  let clipboardUnlocked = false
  const unlockClipboard = () => {
    if (clipboardUnlocked) return
    clipboardUnlocked = true
    navigator.clipboard?.readText?.().catch(() => { })
  }

  document.addEventListener('focusin', (e) => {
    if (isEditable(e.target)) {
      lastFocused = e.target
      unlockClipboard()
    }
  })

  const handlePaste = async () => {

    const target = lastFocused

    if (!isEditable(target)) return

    const text = await readClipboard()

    if (text) {
      insertText(target, text)
    }

  }

  const handleCopy = async () => {

    const target = lastFocused

    if (!isEditable(target)) return

    const text = getSelectedText(target)

    if (text) {
      await writeClipboard(text)
    }

  }

  // CTRL+C / CTRL+V
  window.addEventListener("keydown", async (e) => {

    const ctrl = e.ctrlKey || e.metaKey

    if (!ctrl) return

    const key = e.key.toLowerCase()

    if (key === "v") {

      e.preventDefault()
      await handlePaste()

    }

    if (key === "c") {

      e.preventDefault()
      await handleCopy()

    }

  })

  // native paste
  window.addEventListener("paste", (e) => {

    const target = lastFocused

    if (!isEditable(target)) return

    const text = e.clipboardData?.getData("text")

    if (text) {
      e.preventDefault()
      insertText(target, text)
    }

  })

  if (!isTouchDevice()) {
    const pasteCatcher = document.createElement('textarea')
    pasteCatcher.setAttribute('readonly', 'true')
    pasteCatcher.setAttribute('tabindex', '-1')
    pasteCatcher.setAttribute('aria-hidden', 'true')
    pasteCatcher.style.position = 'fixed'
    pasteCatcher.style.opacity = '0'
    pasteCatcher.style.left = '-9999px'
    pasteCatcher.style.pointerEvents = 'none'

    document.body.appendChild(pasteCatcher)

    window.addEventListener('keydown', (e) => {
      const ctrl = e.ctrlKey || e.metaKey

      if (ctrl && e.key.toLowerCase() === 'v') {
        pasteCatcher.focus()

        setTimeout(() => {
          const text = pasteCatcher.value

          if (text && isEditable(lastFocused)) {
            insertText(lastFocused, text)
          }

          pasteCatcher.value = ''
        }, 10)
      }
    })
  }

}