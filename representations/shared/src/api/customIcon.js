import { BASE_URL } from './client.js'

const CUSTOM_PREFIX = 'custom:'

export const isCustomIcon = (icon) =>
    typeof icon === 'string' && icon.startsWith(CUSTOM_PREFIX)

export const customIconId = (icon) => {
    if (!isCustomIcon(icon)) return null
    return icon.slice(CUSTOM_PREFIX.length)
}

export const customIconPath = (icon) => {
    const id = customIconId(icon)
    if (!id) return null
    return `/custom-icon/${id}/file`
}

export const customIconFileUrl = (icon) => {
    const path = customIconPath(icon)
    return path ? `${BASE_URL}${path}` : null
}

export const iconDisplayLabel = (icon, fallback = '📁') => {
    if (!icon) return fallback
    if (isCustomIcon(icon)) return fallback
    return icon
}

/** Иконка площадки важнее иконки категории. */
export const resolveAccountIcon = (resourceIcon, categoryIcon) =>
    resourceIcon || categoryIcon || null

export function createCustomIconApi(client) {
    return {
        getList: () =>
            client.request('/custom-icon/list', {
                errorMessage: 'Не удалось загрузить иконки',
            }),

        upload: (file, { label = null, fallbackEmoji = '📁' } = {}) => {
            const body = new FormData()
            body.append('file', file)
            if (label) body.append('label', label)
            body.append('fallback_emoji', fallbackEmoji)
            return client.request('/custom-icon', {
                method: 'POST',
                body,
                errorMessage: 'Не удалось загрузить иконку',
            })
        },

        delete: (iconId) =>
            client.request(`/custom-icon/${iconId}`, {
                method: 'DELETE',
                errorMessage: 'Не удалось удалить иконку',
            }),
    }
}
