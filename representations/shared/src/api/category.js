/** Списочные ручки отвечают то массивом, то {data: [...]}. */
export const asList = (payload) => (Array.isArray(payload) ? payload : payload?.data || [])

export function createCategoryApi(client) {
    const api = {
        getList: () =>
            client.request('/category/list', {
                errorMessage: 'Не удалось загрузить категории',
            }),

        getChildren: (categoryId) =>
            client.request(`/category/${categoryId}/children`, {
                errorMessage: 'Не удалось загрузить подкатегории',
            }),

        getDetail: (categoryId) =>
            client.request(`/category/${categoryId}`, {
                errorMessage: 'Не удалось загрузить категорию',
            }),

        /** Плоский список всех категорий; на старом бэкенде без /category/all собираем сами. */
        async getAll() {
            const res = await client.raw('/category/all')
            if (res.ok) return res.json()

            const flat = []
            for (const root of asList(await api.getList())) {
                flat.push(root)
                try {
                    flat.push(...asList(await api.getChildren(root.id)))
                } catch {
                    // подкатегории необязательны
                }
            }
            return flat
        },

        create: (category) =>
            client.request('/category', {
                method: 'POST',
                body: category,
                errorMessage: 'Не удалось создать категорию',
            }),

        update: (categoryId, category) =>
            client.request(`/category/${categoryId}`, {
                method: 'PUT',
                body: category,
                errorMessage: 'Не удалось обновить категорию',
            }),

        reorder: (orderList) =>
            client.request('/category/reorder', {
                method: 'PUT',
                body: orderList,
                errorMessage: 'Не удалось сохранить порядок',
            }),

        delete: (categoryId, transfer = true) =>
            client.request(`/category/${categoryId}?transfer=${transfer}`, {
                method: 'DELETE',
                errorMessage: 'Не удалось удалить категорию',
            }),
    }

    return api
}
