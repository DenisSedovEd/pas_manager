/** Тело запроса одинаково для create и update — раньше дублировалось 4 раза. */
const toPayload = (account) => ({
    category_id: account.category_id,
    resource_id: account.resource_id,
    login: account.login,
    password: account.password,
    email: account.email || null,
    phone: account.phone || null,
    label: account.label || null,
})

export function createAccountApi(client) {
    return {
        getList: (categoryId) =>
            client.request(`/account/list/${categoryId}`, {
                errorMessage: 'Не удалось загрузить аккаунты',
            }),

        getDetail: (accountId) =>
            client.request(`/account/${accountId}`, {
                errorMessage: 'Не удалось загрузить аккаунт',
            }),

        create: (account) =>
            client.request('/account', {
                method: 'POST',
                body: toPayload(account),
                errorMessage: 'Не удалось создать аккаунт',
            }),

        update: (accountId, account) =>
            client.request(`/account/${accountId}`, {
                method: 'PUT',
                body: toPayload(account),
                errorMessage: 'Не удалось обновить аккаунт',
            }),

        delete: (accountId) =>
            client.request(`/account/${accountId}`, {
                method: 'DELETE',
                errorMessage: 'Не удалось удалить аккаунт',
            }),

        reorder: (orderList) =>
            client.request('/account/reorder', {
                method: 'PUT',
                body: orderList,
                errorMessage: 'Не удалось сохранить порядок',
            }),

        getSuggestions: () =>
            client.request('/account/suggestions', {
                errorMessage: 'Не удалось загрузить подсказки',
            }),

        search: (query) =>
            client.request(`/account/search?q=${encodeURIComponent(query)}`, {
                errorMessage: 'Ошибка поиска',
            }),
    }
}
