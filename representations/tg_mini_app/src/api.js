import { createApi, initDataAuth, blobIconSource } from '@pas/shared/api/index.js'

// initData читаем лениво: Telegram-скрипт может ещё не быть готов на момент импорта
const getInitData = () => window.Telegram?.WebApp?.initData ?? ''

// Mini App: авторизация заголовком, поэтому кастомные иконки тянем fetch'ем в blob.
export const api = createApi({
    auth: initDataAuth(getInitData),
    iconSource: blobIconSource,
})

export const {
    accountApi,
    categoryApi,
    resourceApi,
    customFieldApi,
    customIconApi,
    setSessionExpiredHandler,
} = api

// Хелперы — реэкспорт, чтобы компоненты импортировали всё из одного места
export {
    asList,
    pickDefaultResource,
    isCustomIcon,
    customIconId,
    customIconFileUrl,
    iconDisplayLabel,
    resolveAccountIcon,
} from '@pas/shared/api/index.js'
