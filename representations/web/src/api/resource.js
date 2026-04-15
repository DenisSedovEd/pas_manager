const BASE_URL = '/pas-manager/v1'

function bearer() {
    const t = sessionStorage.getItem('web_token')
    return t ? `Bearer ${t}` : ''
}

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
