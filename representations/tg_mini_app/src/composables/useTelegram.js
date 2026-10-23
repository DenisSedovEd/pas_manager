export function useTelegram() {
  const tg = window.Telegram?.WebApp ?? null
  const bio = tg?.BiometricManager ?? null

  const initApp = () => {
    if (!tg) return
    tg.ready()
    tg.expand()
  }

  return {
    tg,
    bio,
    initApp,
    initData: tg?.initData ?? '',
  }
}
