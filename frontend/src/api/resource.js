const BASE_URL = '/pas-manager/v1';

export const resourceApi = {
    async getList(initData) {
        const response = await fetch(`${BASE_URL}/resource/list`, {
            headers: {'Authorization': initData}
        });
        if (!response.ok) throw new Error('Failed to fetch resources');
        return response.json();
    },

    async getByName(initData, name) {
        const response = await fetch(
            `${BASE_URL}/resource/by-name/${encodeURIComponent(name)}`,
            {headers: {'Authorization': initData}}
        );
        if (!response.ok) throw new Error('Resource not found');
        return response.json();
    },

    async getDetail(initData, resourceId) {
        const response = await fetch(`${BASE_URL}/resource/${resourceId}`, {
            headers: {'Authorization': initData}
        });
        if (!response.ok) throw new Error('Failed to fetch resource');
        return response.json();
    },

    async create(initData, resource) {
        const response = await fetch(`${BASE_URL}/resource`, {
            method: 'POST',
            headers: {
                'Authorization': initData,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(resource)
        });
        if (!response.ok) throw new Error('Failed to create resource');
        return response.json();
    },
};
