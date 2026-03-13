const BASE_URL = '/pas-manager/v1';

export const platformApi = {
    async getList(initData) {
        const response = await fetch(`${BASE_URL}/platform/list`, {
            headers: {'Authorization': initData}
        });
        if (!response.ok) throw new Error('Failed to fetch platforms');
        return response.json();
    },

    async getDetail(initData, platformId) {
        const response = await fetch(`${BASE_URL}/platform/${platformId}`, {
            headers: {'Authorization': initData}
        });
        if (!response.ok) throw new Error('Failed to fetch platform');
        return response.json();
    },

    async create(initData, platform) {
        const response = await fetch(`${BASE_URL}/platform`, {
            method: 'POST',
            headers: {
                'Authorization': initData,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(platform)
        });
        if (!response.ok) throw new Error('Failed to create platform');
        return response.json();
    },

    async update(initData, platformId, platform) {
        const response = await fetch(`${BASE_URL}/platform/${platformId}`, {
            method: 'PUT',
            headers: {
                'Authorization': initData,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(platform)
        });
        if (!response.ok) throw new Error('Failed to update platform');
        return response.json();
    },

    async reorder(initData, orderList) {
        const response = await fetch(`${BASE_URL}/platform/reorder`, {
            method: 'PUT',
            headers: {
                'Authorization': initData,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderList)
        });

        if (!response.ok) {
            throw new Error('Failed to update order');
        }

        return await response.json();
    },


    async delete(initData, platformId, transfer = true) {
        const response = await fetch(`${BASE_URL}/platform/${platformId}?transfer=${transfer}`, {
            method: 'DELETE',
            headers: {'Authorization': initData}
        });
        if (!response.ok) throw new Error('Failed to delete platform');
        return response.json();
    }
};