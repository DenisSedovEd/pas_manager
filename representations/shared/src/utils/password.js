// Без похожих друг на друга символов (0/O, 1/l/I) — пароль часто перепечатывают руками
const CHARSET = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789-_.@%^+'
const DEFAULT_LENGTH = 16

export function generatePassword(length = DEFAULT_LENGTH) {
    const values = new Uint32Array(length)
    crypto.getRandomValues(values)
    return Array.from(values, (v) => CHARSET[v % CHARSET.length]).join('')
}
