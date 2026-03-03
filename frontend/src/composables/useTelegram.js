import { ref } from 'vue';

export function useTelegram() {
  const tg = window.Telegram.WebApp;
  const bio = tg.BiometricManager;

  const initApp = () => {
    tg.ready();
    tg.expand();
  };

  const closeApp = () => tg.close();

  return { tg, bio, initApp, closeApp, initData: tg.initData };
}