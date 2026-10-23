/** Системная площадка, на которую переносятся аккаунты при удалении прочих. */
export const DEFAULT_RESOURCE_NAME = 'Без площадки'

/** Раньше этот выбор был скопирован в оба App.vue по два раза. */
export const pickDefaultResource = (resources = []) =>
    resources.find((r) => r.resource_name === DEFAULT_RESOURCE_NAME) || resources[0] || null

export function createResourceApi(client) {
    return {
        getList: () =>
            client.request('/resource/list', {
                errorMessage: 'Не удалось загрузить площадки',
            }),

        getDetail: (resourceId) =>
            client.request(`/resource/${resourceId}`, {
                errorMessage: 'Не удалось загрузить площадку',
            }),

        create: (resource) =>
            client.request('/resource', {
                method: 'POST',
                body: resource,
                errorMessage: 'Не удалось создать площадку',
            }),

        update: (resourceId, resource) =>
            client.request(`/resource/${resourceId}`, {
                method: 'PUT',
                body: resource,
                errorMessage: 'Не удалось обновить площадку',
            }),

        delete: (resourceId) =>
            client.request(`/resource/${resourceId}`, {
                method: 'DELETE',
                errorMessage: 'Не удалось удалить площадку',
            }),
    }
}
