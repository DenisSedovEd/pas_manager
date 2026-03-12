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
    } catch {}

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

    if (!text) return

    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text)
        return
      }
    } catch {}

    if (tg?.writeTextToClipboard) {
      tg.writeTextToClipboard(text)
    }
  }

  // remember focused element
  document.addEventListener("focusin", (e) => {

    if (isEditable(e.target)) {
      lastFocused = e.target
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

  // unlock clipboard API
  document.addEventListener("click", () => {

    navigator.clipboard?.readText?.().catch(() => {})

  }, { once: true })

  // TELEGRAM DESKTOP WORKAROUND

  const pasteCatcher = document.createElement("textarea")

  pasteCatcher.style.position = "fixed"
  pasteCatcher.style.opacity = "0"
  pasteCatcher.style.left = "-9999px"
  pasteCatcher.style.pointerEvents = "none"

  document.body.appendChild(pasteCatcher)

  window.addEventListener("keydown", (e) => {

    const ctrl = e.ctrlKey || e.metaKey

    if (ctrl && e.key.toLowerCase() === "v") {

      pasteCatcher.focus()

      setTimeout(() => {

        const text = pasteCatcher.value

        if (text && isEditable(lastFocused)) {
          insertText(lastFocused, text)
        }

        pasteCatcher.value = ""

      }, 10)

    }

  })

}