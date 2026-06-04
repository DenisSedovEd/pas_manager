import { BASE_URL } from './client.js'

export const accountApi = {
    async getList(categoryId) {
        const res = await fetch(`${BASE_URL}/account/list/${categoryId}`, {
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to fetch accounts')
        return res.json()
    },

    async getDetail(accountId) {
        const res = await fetch(`${BASE_URL}/account/${accountId}`, {
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to fetch account')
        return res.json()
    },

    async create(account) {
        const res = await fetch(`${BASE_URL}/account`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
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
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
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
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to delete account')
        return res.json()
    },

    async reorder(orderList) {
        const res = await fetch(`${BASE_URL}/account/reorder`, {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderList),
        })
        if (!res.ok) throw new Error('Failed to reorder')
        return res.json()
    },

    async getSuggestions() {
        const res = await fetch(`${BASE_URL}/account/suggestions`, {
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to fetch suggestions')
        return res.json()
    },

    async search(query) {
        const res = await fetch(`${BASE_URL}/account/search?q=${encodeURIComponent(query)}`, {
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to search')
        return res.json()
    },
}
