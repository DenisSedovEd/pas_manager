const BASE_URL = '/pas-manager/v1';

export const categoryApi = {
    async getList(initData) {
        const response = await fetch(`${BASE_URL}/category/list`, {
            headers: {'Authorization': initData}
        });
        if (!response.ok) throw new Error('Failed to fetch categories');
        return response.json();
    },

    async getChildren(initData, categoryId) {
        const response = await fetch(`${BASE_URL}/category/${categoryId}/children`, {
            headers: {'Authorization': initData}
        });
        if (!response.ok) throw new Error('Failed to fetch children');
        return response.json();
    },

    async getDetail(initData, categoryId) {
        const response = await fetch(`${BASE_URL}/category/${categoryId}`, {
            headers: {'Authorization': initData}
        });
        if (!response.ok) throw new Error('Failed to fetch category');
        return response.json();
    },

    async create(initData, category) {
        const response = await fetch(`${BASE_URL}/category`, {
            method: 'POST',
            headers: {
                'Authorization': initData,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(category)
        });
        if (!response.ok) throw new Error('Failed to create category');
        return response.json();
    },

    async update(initData, categoryId, category) {
        const response = await fetch(`${BASE_URL}/category/${categoryId}`, {
            method: 'PUT',
            headers: {
                'Authorization': initData,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(category)
        });
        if (!response.ok) throw new Error('Failed to update category');
        return response.json();
    },

    async reorder(initData, orderList) {
        const response = await fetch(`${BASE_URL}/category/reorder`, {
            method: 'PUT',
            headers: {
                'Authorization': initData,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderList)
        });
        if (!response.ok) throw new Error('Failed to update order');
        return response.json();
    },

    async delete(initData, categoryId, transfer = true) {
        const response = await fetch(`${BASE_URL}/category/${categoryId}?transfer=${transfer}`, {
            method: 'DELETE',
            headers: {'Authorization': initData}
        });
        if (!response.ok) throw new Error('Failed to delete category');
        return response.json();
    }
};
