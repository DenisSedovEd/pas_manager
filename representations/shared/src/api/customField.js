export function createCustomFieldApi(client) {
    return {
        getList: () =>
            client.request('/custom-field/list', {
                errorMessage: 'Не удалось загрузить кастомные поля',
            }),

        create: (field) =>
            client.request('/custom-field', {
                method: 'POST',
                body: field,
                errorMessage: 'Не удалось создать поле',
            }),

        getValues: (entityType, entityId) =>
            client.request(`/custom-field/values/${entityType}/${entityId}`, {
                errorMessage: 'Не удалось загрузить значения полей',
            }),

        replaceValues: (entityType, entityId, fields) =>
            client.request(`/custom-field/values/${entityType}/${entityId}`, {
                method: 'PUT',
                body: { fields },
                errorMessage: 'Не удалось сохранить значения полей',
            }),
    }
}
