import { createApi, cookieAuth, directIconSource } from '@pas/shared/api/index.js'

// Web SPA: сессия в cookie, кастомные иконки грузятся обычным <img src>.
export const api = createApi({
    auth: cookieAuth,
    iconSource: directIconSource,
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
