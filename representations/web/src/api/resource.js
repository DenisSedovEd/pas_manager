import { BASE_URL, bearer } from './client.js'

export const resourceApi = {
    async getList() {
        const res = await fetch(`${BASE_URL}/resource/list`, {
            headers: { Authorization: bearer() },
        })
        if (!res.ok) throw new Error('Failed to fetch resources')
        return res.json()
    },

    async getDetail(resourceId) {
        const res = await fetch(`${BASE_URL}/resource/${resourceId}`, {
            headers: { Authorization: bearer() },
        })
        if (!res.ok) throw new Error('Failed to fetch resource')
        return res.json()
    },

    async create(resource) {
        const res = await fetch(`${BASE_URL}/resource`, {
            method: 'POST',
            headers: { Authorization: bearer(), 'Content-Type': 'application/json' },
            body: JSON.stringify(resource),
        })
        if (!res.ok) throw new Error('Failed to create resource')
        return res.json()
    },
}
