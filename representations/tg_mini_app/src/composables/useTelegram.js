export function useTelegram() {
  const tg = window.Telegram?.WebApp ?? null
  const bio = tg?.BiometricManager ?? null

  const initApp = () => {
    if (!tg) return
    tg.ready()
    tg.expand()
  }

  const setupSettingsButton = (onShowCallback) => {
    if (!tg) return
    tg.SettingsButton.show()
    tg.onEvent('settingsButtonClicked', onShowCallback)
  }

  const hideSettingsButton = () => {
    if (!tg) return
    tg.SettingsButton.hide()
    tg.offEvent('settingsButtonClicked')
  }

  const showAlert = (message) => {
    if (tg) tg.showAlert(message)
    else alert(message)
  }

  const closeApp = () => {
    if (tg) tg.close()
  }

  return {
    tg,
    bio,
    isAvailable: !!tg,
    initApp,
    closeApp,
    setupSettingsButton,
    hideSettingsButton,
    haptic: tg?.HapticFeedback ?? null,
    showAlert,
    initData: tg?.initData ?? '',
  }
}
