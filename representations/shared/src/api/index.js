import { createApiClient } from './client.js'
import { createAccountApi } from './account.js'
import { createCategoryApi } from './category.js'
import { createResourceApi } from './resource.js'
import { createCustomFieldApi } from './customField.js'
import { createCustomIconApi } from './customIcon.js'
import { directIconSource } from './iconSource.js'

export { BASE_URL, createApiClient } from './client.js'
export { cookieAuth, initDataAuth } from './auth.js'
export { asList } from './category.js'
export { DEFAULT_RESOURCE_NAME, pickDefaultResource } from './resource.js'
export { directIconSource, blobIconSource } from './iconSource.js'
export {
    isCustomIcon,
    customIconId,
    customIconPath,
    customIconFileUrl,
    iconDisplayLabel,
    resolveAccountIcon,
} from './customIcon.js'

/**
 * Собирает API для одного представления.
 *
 * @param auth              cookieAuth | initDataAuth(getInitData)
 * @param onSessionExpired  реакция на 401
 * @param iconSource        directIconSource | blobIconSource
 */
export function createApi({ auth, onSessionExpired = null, iconSource = directIconSource } = {}) {
    const client = createApiClient({ auth, onSessionExpired })

    return {
        client,
        setSessionExpiredHandler: client.setSessionExpiredHandler,
        accountApi: createAccountApi(client),
        categoryApi: createCategoryApi(client),
        resourceApi: createResourceApi(client),
        customFieldApi: createCustomFieldApi(client),
        customIconApi: createCustomIconApi(client),
        iconSource: iconSource(client),
    }
}
