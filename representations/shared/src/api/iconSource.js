import { customIconPath } from './customIcon.js'

/**
 * Здесь представления расходятся по-настоящему:
 *  - web шлёт cookie автоматически, значит годится обычный <img src>;
 *  - mini app обязан передать заголовок Authorization, поэтому картинку
 *    приходится тянуть fetch'ем и отдавать blob-URL.
 *
 * Оба адаптера возвращают { src, release } — release освобождает blob-URL
 * (для web это no-op), вызывать при смене иконки и на unmount.
 */

const NOOP_RELEASE = () => {}

export const directIconSource = (client) => ({
    async load(icon) {
        const path = customIconPath(icon)
        if (!path) return null
        return { src: client.buildUrl(path), release: NOOP_RELEASE }
    },
})

export const blobIconSource = (client) => ({
    async load(icon) {
        const path = customIconPath(icon)
        if (!path) return null

        const res = await client.raw(path)
        if (!res.ok) throw new Error('Не удалось загрузить иконку')

        const blobUrl = URL.createObjectURL(await res.blob())
        return { src: blobUrl, release: () => URL.revokeObjectURL(blobUrl) }
    },
})
