import { BASE_URL } from './client.js'

const CUSTOM_PREFIX = 'custom:'

export const isCustomIcon = (icon) =>
  typeof icon === 'string' && icon.startsWith(CUSTOM_PREFIX)

export const customIconId = (icon) => {
  if (!isCustomIcon(icon)) return null
  return icon.slice(CUSTOM_PREFIX.length)
}

export const customIconFileUrl = (icon) => {
  const id = customIconId(icon)
  if (!id) return null
  return `${BASE_URL}/custom-icon/${id}/file`
}

export const iconDisplayLabel = (icon, fallback = '📁') => {
  if (!icon) return fallback
  if (isCustomIcon(icon)) return fallback
  return icon
}

export const customIconApi = {
  async getList() {
    const res = await fetch(`${BASE_URL}/custom-icon/list`, {
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to fetch custom icons')
    return res.json()
  },

  async upload(file, { label = null, fallbackEmoji = '📁' } = {}) {
    const body = new FormData()
    body.append('file', file)
    if (label) body.append('label', label)
    body.append('fallback_emoji', fallbackEmoji)
    const res = await fetch(`${BASE_URL}/custom-icon`, {
      method: 'POST',
      credentials: 'include',
      body,
    })
    if (!res.ok) {
      const detail = await res.json().catch(() => null)
      throw new Error(detail?.detail || 'Failed to upload icon')
    }
    return res.json()
  },

  async delete(iconId) {
    const res = await fetch(`${BASE_URL}/custom-icon/${iconId}`, {
      method: 'DELETE',
      credentials: 'include',
    })
    if (!res.ok) throw new Error('Failed to delete icon')
    return res.json()
  },
}
