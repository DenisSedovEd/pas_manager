import { BASE_URL } from './client.js'

export const resourceApi = {
    async getList() {
        const res = await fetch(`${BASE_URL}/resource/list`, {
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to fetch resources')
        return res.json()
    },

    async getDetail(resourceId) {
        const res = await fetch(`${BASE_URL}/resource/${resourceId}`, {
            credentials: 'include',
        })
        if (!res.ok) throw new Error('Failed to fetch resource')
        return res.json()
    },

    async create(resource) {
        const res = await fetch(`${BASE_URL}/resource`, {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(resource),
        })
        if (!res.ok) throw new Error('Failed to create resource')
        return res.json()
    },
}
