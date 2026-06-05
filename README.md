# 🔐 PasManage

> Личный зашифрованный менеджер паролей с управлением через Telegram

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?style=flat&logo=vuedotjs&logoColor=white)](https://vuejs.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)

---

## ✨ Что это

**PasManage** — самохостируемый менеджер паролей только для вас. Никаких облачных хранилищ с чужими ключами. Все данные зашифрованы на основе вашего **мастер-пароля** — даже владелец сервера не имеет к ним доступа.

Три способа использования:

| Интерфейс | Описание |
|---|---|
| 🤖 **Telegram Bot** | Классический бот для быстрого доступа с телефона |
| 📱 **Telegram Mini App** | Веб-приложение прямо внутри Telegram |
| 🌐 **Web SPA** | Браузерный интерфейс с отдельной авторизацией |

---

## 🛡️ Безопасность

- **AES-256** шифрование всех паролей
- **Argon2** хэширование мастер-пароля
- Ваш мастер-пароль **никогда не хранится** — только его хэш
- Верификация Telegram initData через HMAC-SHA256
- Сессии с настраиваемым TTL
- Поддержка биометрической аутентификации (в Mini App)

---

## 🏗️ Архитектура

```
pas_manage/
├── backend/
│   ├── api/            # FastAPI роутеры (REST API)
│   ├── core/           # Конфиг, БД, безопасность, сессии
│   ├── models/         # SQLAlchemy модели
│   ├── repositories/   # Слой работы с БД и шифрованием
│   ├── schemas/        # Pydantic схемы
│   ├── services/       # Бизнес-логика
│   └── tg_bot/         # Telegram Bot хэндлеры
├── representations/
│   ├── tg_mini_app/    # Vue 3 Mini App для Telegram
│   └── web/            # Vue 3 Web SPA
├── alembic/            # Миграции БД
├── Dockerfile
└── docker-compose.yml
```

**Стек:**
- 🐍 Python 3.11+ · FastAPI · SQLAlchemy · Alembic · aiosqlite
- 🎨 Vue 3 · Vite
- 🐳 Docker · Cloudflare Tunnel
- 📦 `uv` для управления зависимостями

---

## 🚀 Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/DenisSedovEd/pas_manage.git
cd pas_manage
```

### 2. Создать `.env` файл

```env
# Telegram
TG__USER_ID=123456789
TG__TELEGRAM_TOKEN=your_bot_token_here

# Приложение
APP__DELETE_TIMEOUT_SECONDS=30
APP__SESSION_TTL=3600
APP__TUNNEL_TOKEN=your_cloudflare_tunnel_token
APP__ADMIN_ID=123456789

# Шифрование
CRYPTO__KEY_LENGTH=32
CRYPTO__SALT_SIZE=16
CRYPTO__ITERATIONS=200000
```

### 3. Запустить через Docker

```bash
docker compose up -d
```

При первом запуске автоматически применятся миграции Alembic и поднимется весь стек: FastAPI API + Cloudflare Tunnel.

---

## ⚙️ Переменные окружения

| Переменная | Описание |
|---|---|
| `TG__USER_ID` | Ваш Telegram user ID (только вы имеете доступ) |
| `TG__TELEGRAM_TOKEN` | Токен бота от [@BotFather](https://t.me/BotFather) |
| `APP__DELETE_TIMEOUT_SECONDS` | Через сколько секунд удаляются сообщения бота |
| `APP__SESSION_TTL` | Время жизни сессии (секунды) |
| `APP__TUNNEL_TOKEN` | Токен Cloudflare Tunnel для HTTPS без сервера |
| `APP__ADMIN_ID` | Telegram ID администратора |
| `CRYPTO__KEY_LENGTH` | Длина ключа шифрования (байт) |
| `CRYPTO__SALT_SIZE` | Размер соли (байт) |
| `CRYPTO__ITERATIONS` | Количество итераций PBKDF2 |

---

## 🔧 Локальная разработка

```bash
# Установить зависимости
uv sync

# Применить миграции
uv run alembic upgrade head

# Запустить API
uv run python -m main

# Запустить Telegram бота отдельно
uv run python -m bot
```

Фронтенд (Mini App / Web):

```bash
cd representations/tg_mini_app  # или representations/web
npm install
npm run dev
```

---

## 📦 Деплой

Проект деплоится автоматически через **GitHub Actions** при пуше в `master`:

1. 🏗️ Собирается Docker-образ и публикуется на Docker Hub (`denissedoved/pas_manager:latest`)
2. 🚀 По SSH на сервер — `docker compose up -d`

Для настройки деплоя добавьте в GitHub Secrets:

| Secret | Описание |
|---|---|
| `DOCKER_USERNAME` | Логин Docker Hub |
| `DOCKER_PASSWORD` | Пароль Docker Hub |
| `DEPLOY_HOST` | IP / hostname сервера |
| `DEPLOY_USER` | SSH-пользователь |
| `SSH_PRIVATE_KEY` | Приватный SSH-ключ |

---

## 🗂️ Структура данных

- **Аккаунты** — логин + зашифрованный пароль + URL + иконка
- **Категории** — организация аккаунтов с поддержкой вложенности
- **Ресурсы** — произвольные зашифрованные заметки

Все чувствительные поля хранятся в зашифрованном виде в SQLite.

---

## ⚠️ Важно

Мастер-пароль **нельзя восстановить**. Если вы его забудете — все зашифрованные данные будут недоступны. Храните его надёжно.
