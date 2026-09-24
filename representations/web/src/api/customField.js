import { BASE_URL } from './client.js'

export const customFieldApi = {
  async getList() {
    const res = await fetch(`${BASE_URL}/custom-field/list`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch custom fields')
    return res.json()
  },

  async create(field) {
    const res = await fetch(`${BASE_URL}/custom-field`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(field),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to create custom field')
    }
    return res.json()
  },

  async getValues(entityType, entityId) {
    const res = await fetch(
      `${BASE_URL}/custom-field/values/${entityType}/${entityId}`,
      { credentials: 'include' },
    )
    if (!res.ok) throw new Error('Failed to fetch custom field values')
    return res.json()
  },

  async replaceValues(entityType, entityId, fields) {
    const res = await fetch(
      `${BASE_URL}/custom-field/values/${entityType}/${entityId}`,
      {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fields }),
      },
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to save custom field values')
    }
    return res.json()
  },
}
