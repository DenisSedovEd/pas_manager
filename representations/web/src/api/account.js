const BASE_URL = '/pas-manager/v1'

function bearer() {
    const t = sessionStorage.getItem('web_token')
    return t ? `Bearer ${t}` : ''
}

export const accountApi = {
    async getList(categoryId) {
        const res = await fetch(`${BASE_URL}/account/list/${categoryId}`, {
            headers: { Authorization: bearer() },
        })
        if (!res.ok) throw new Error('Failed to fetch accounts')
        return res.json()
    },

    async getDetail(accountId) {
        const res = await fetch(`${BASE_URL}/account/${accountId}`, {
            headers: { Authorization: bearer() },
        })
        if (!res.ok) throw new Error('Failed to fetch account')
        return res.json()
    },

    async create(account) {
        const res = await fetch(`${BASE_URL}/account`, {
            method: 'POST',
            headers: { Authorization: bearer(), 'Content-Type': 'application/json' },
            body: JSON.stringify({
                category_id: account.category_id,
                resource_id: account.resource_id,
                login: account.login,
                password: account.password,
                email: account.email || null,
                phone: account.phone || null,
                label: account.label || null,
            }),
        })
        if (!res.ok) throw new Error('Failed to create account')
        return res.json()
    },

    async update(accountId, account) {
        const res = await fetch(`${BASE_URL}/account/${accountId}`, {
            method: 'PUT',
            headers: { Authorization: bearer(), 'Content-Type': 'application/json' },
            body: JSON.stringify({
                category_id: account.category_id,
                resource_id: account.resource_id,
                login: account.login,
                password: account.password,
                email: account.email || null,
                phone: account.phone || null,
                label: account.label || null,
            }),
        })
        if (!res.ok) throw new Error('Failed to update account')
        return res.json()
    },

    async delete(accountId) {
        const res = await fetch(`${BASE_URL}/account/${accountId}`, {
            method: 'DELETE',
            headers: { Authorization: bearer() },
        })
        if (!res.ok) throw new Error('Failed to delete account')
        return res.json()
    },

    async reorder(orderList) {
        const res = await fetch(`${BASE_URL}/account/reorder`, {
            method: 'PUT',
            headers: { Authorization: bearer(), 'Content-Type': 'application/json' },
            body: JSON.stringify(orderList),
        })
        if (!res.ok) throw new Error('Failed to reorder')
        return res.json()
    },

    async getSuggestions() {
        const res = await fetch(`${BASE_URL}/account/suggestions`, {
            headers: { Authorization: bearer() },
        })
        if (!res.ok) throw new Error('Failed to fetch suggestions')
        return res.json()
    },
}
