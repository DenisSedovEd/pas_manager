const BASE_URL = '/pas-manager';

export const vaultApi = {
  async getPlatforms(initData) {
    const res = await fetch(`${BASE_URL}/platforms`, {
      headers: { 'Authorization': initData }
    });
    if (!res.ok) throw new Error('Ошибка загрузки платформ');
    return res.json();
  }
};