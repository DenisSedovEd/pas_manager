const BASE_URL = '/pas-manager';

export const vaultApi = {
  async getCategories(initData) {
    const res = await fetch(`${BASE_URL}/categories`, {
      headers: { 'Authorization': initData }
    });
    if (!res.ok) throw new Error('Ошибка загрузки категорий');
    return res.json();
  }
};