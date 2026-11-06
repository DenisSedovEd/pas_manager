import config from '../config.json'

// Без похожих друг на друга символов (0/O, 1/l/I) — пароль часто перепечатывают руками
const buildCharset = () => {
    const excluded = new Set(config.password.excludedChars)
    const base = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    const safe = [...base].filter((c) => !excluded.has(c)).join('')
    return safe + config.password.specialChars
}

const CHARSET = buildCharset()
const DEFAULT_LENGTH = config.password.length

export function generatePassword(length = DEFAULT_LENGTH) {
    const values = new Uint32Array(length)
    crypto.getRandomValues(values)
    return Array.from(values, (v) => CHARSET[v % CHARSET.length]).join('')
}
