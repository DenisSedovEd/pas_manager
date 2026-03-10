const BASE_URL = '/pas-manager/v1';

export const platformApi = {
  async getList(initData) {
    const response = await fetch(`${BASE_URL}/platform/list`, {
      headers: { 'Authorization': initData }
    });
    if (!response.ok) throw new Error('Failed to fetch platforms');
    return response.json();
  },

  async create(initData, platform) {
    const response = await fetch(`${BASE_URL}/platform`, {
      method: 'POST',
      headers: {
        'Authorization': initData,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: platform.name,
        icon: platform.icon,
        description: platform.description || null
      })
    });
    if (!response.ok) throw new Error('Failed to create platform');
    return response.json();
  }
};