const BASE_URL = '/pas-manager/v1';

export const accountApi = {
  async getList(initData, platformId) {
    const response = await fetch(`${BASE_URL}/account/list/${platformId}`, {
      headers: { 'Authorization': initData }
    });
    if (!response.ok) throw new Error('Failed to fetch accounts');
    return response.json();
  },

  async getDetail(initData, accountId) {
    const response = await fetch(`${BASE_URL}/account/${accountId}`, {
      headers: { 'Authorization': initData }
    });
    if (!response.ok) throw new Error('Failed to fetch account');
    return response.json();
  },

  async create(initData, account) {
    const response = await fetch(`${BASE_URL}/account`, {
      method: 'POST',
      headers: {
        'Authorization': initData,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        platform_id: account.platform_id,  // ← UUID строка
        login: account.login,
        password: account.password,
        email: account.email || null,
        phone: account.phone || null,
        label: account.label || null
      })
    });
    if (!response.ok) throw new Error('Failed to create account');
    return response.json();
  },

  async update(initData, accountId, account) {
    const response = await fetch(`${BASE_URL}/account/${accountId}`, {
      method: 'PUT',
      headers: {
        'Authorization': initData,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        platform_id: account.platform_id,  // ← UUID строка
        login: account.login,
        password: account.password,
        email: account.email || null,
        phone: account.phone || null,
        label: account.label || null
      })
    });
    if (!response.ok) throw new Error('Failed to update account');
    return response.json();
  },

  async delete(initData, accountId) {
    const response = await fetch(`${BASE_URL}/account/${accountId}`, {
      method: 'DELETE',
      headers: { 'Authorization': initData }
    });
    if (!response.ok) throw new Error('Failed to delete account');
    return response.json();
  }
};