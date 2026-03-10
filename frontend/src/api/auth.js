const BASE_URL = '/pas-manager/v1';

export const authApi = {
  async getStatus(initData) {
    const response = await fetch(`${BASE_URL}/main/auth/status`, {
      headers: { 'Authorization': initData }
    });
    return response.json();
  },

  async unlockWithPassword(initData, masterPassword) {
    const response = await fetch(`${BASE_URL}/main/auth/unlock`, {
      method: 'POST',
      headers: {
        'Authorization': initData,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ master_password: masterPassword })
    });
    return response.json();
  },

  async unlockWithBiometric(initData, bioToken) {
    const response = await fetch(`${BASE_URL}/main/auth/unlock-biometric`, {
      method: 'POST',
      headers: {
        'Authorization': initData,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ bio_token: bioToken })
    });
    return response.json();
  },

  async logout(initData) {
    const response = await fetch(`${BASE_URL}/main/auth/logout`, {
      method: 'POST',
      headers: { 'Authorization': initData }
    });
    return response.json();
  }
};