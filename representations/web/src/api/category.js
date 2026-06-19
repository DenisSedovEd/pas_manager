import { BASE_URL } from './client.js'

export const categoryApi = {
    async getList() {
        const res = await fetch(`${BASE_URL}/category/list`, {
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to fetch categories')
        return res.json()
    },

    async getAll() {
        const res = await fetch(`${BASE_URL}/category/all`, {
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to fetch categories')
        return res.json()
    },

    async getDetail(categoryId) {
        const res = await fetch(`${BASE_URL}/category/${categoryId}`, {
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to fetch category')
        return res.json()
    },

    async create(category) {
        const res = await fetch(`${BASE_URL}/category`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(category),
        })
        if (!res.ok) throw new Error('Failed to create category')
        return res.json()
    },

    async update(categoryId, category) {
        const res = await fetch(`${BASE_URL}/category/${categoryId}`, {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(category),
        })
        if (!res.ok) throw new Error('Failed to update category')
        return res.json()
    },

    async reorder(orderList) {
        const res = await fetch(`${BASE_URL}/category/reorder`, {
            method: 'PUT',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderList),
        })
        if (!res.ok) throw new Error('Failed to reorder')
        return res.json()
    },

    async getChildren(categoryId) {
        const res = await fetch(`${BASE_URL}/category/${categoryId}/children`, {
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to fetch children')
        return res.json()
    },

    async delete(categoryId, transfer = true) {
        const res = await fetch(`${BASE_URL}/category/${categoryId}?transfer=${transfer}`, {
            method: 'DELETE',
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to delete category')
        return res.json()
    },
}
