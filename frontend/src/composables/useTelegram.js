import { ref } from 'vue';

export function useTelegram() {
  const tg = window.Telegram.WebApp;
  const bio = tg.BiometricManager;

  const initApp = () => {
    tg.ready();
    tg.expand();
  };

  const setupSettingsButton = (onShowCallback) => {
    tg.SettingsButton.show();
    tg.onEvent('settingsButtonClicked', onShowCallback);
  };

  const hideSettingsButton = () => {
    tg.SettingsButton.hide();
    tg.offEvent('settingsButtonClicked');
  };
  const showAlert = (message) => tg.showAlert(message);
  const haptic = tg.HapticFeedback;

  const closeApp = () => tg.close();

  return {
    tg,
    bio,
    initApp,
    closeApp,
    setupSettingsButton,
    hideSettingsButton,
    haptic,
    showAlert,
    initData: tg.initData
  };
}