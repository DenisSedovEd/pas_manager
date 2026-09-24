const BASE_URL = '/pas-manager/v1'

export const customFieldApi = {
  async getList(initData) {
    const response = await fetch(`${BASE_URL}/custom-field/list`, {
      headers: { Authorization: initData },
    })
    if (!response.ok) throw new Error('Failed to fetch custom fields')
    return response.json()
  },

  async create(initData, field) {
    const response = await fetch(`${BASE_URL}/custom-field`, {
      method: 'POST',
      headers: {
        Authorization: initData,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(field),
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to create custom field')
    }
    return response.json()
  },

  async getValues(initData, entityType, entityId) {
    const response = await fetch(
      `${BASE_URL}/custom-field/values/${entityType}/${entityId}`,
      { headers: { Authorization: initData } },
    )
    if (!response.ok) throw new Error('Failed to fetch custom field values')
    return response.json()
  },

  async replaceValues(initData, entityType, entityId, fields) {
    const response = await fetch(
      `${BASE_URL}/custom-field/values/${entityType}/${entityId}`,
      {
        method: 'PUT',
        headers: {
          Authorization: initData,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fields }),
      },
    )
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to save custom field values')
    }
    return response.json()
  },
}
