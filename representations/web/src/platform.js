import { createDialogHost } from '@pas/shared/platform/dialogHost.js'

// В браузере нативные alert/confirm блокируют поток и выглядят чужеродно —
// используем собственные модалки, их рисует <DialogHost> в App.vue.
export const dialogHost = createDialogHost()

export const webPlatform = {
    alert: dialogHost.alert,
    confirm: dialogHost.confirm,
    haptic: () => {},
}
