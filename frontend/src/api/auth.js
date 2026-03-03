const BASE_URL = '/pas-manager/main';

export const authApi = {
  async getStatus(initData) {
    const res = await fetch(`${BASE_URL}/auth/status`, {
      headers: { 'Authorization': initData }
    });
    return res.json();
  },

  async unlockWithPassword(initData, password) {
    return fetch(`${BASE_URL}/auth/unlock`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': initData },
      body: JSON.stringify({ master_password: password })
    });
  },

  async unlockWithBiometric(initData, token) {
    return fetch(`${BASE_URL}/auth/unlock-biometric`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': initData },
      body: JSON.stringify({ bio_token: token })
    });
  },

  async logout(initData) {
    return fetch(`${BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: { 'Authorization': initData }
    });
  }
};