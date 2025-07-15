[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)
[![Русский](https://img.shields.io/badge/lang-Русский-red.svg)](README.ru.md)

# 🍃 Shinga API
**Ваш мир манги** - REST API для парсинга, хранения и управления мангой

Shinga API - это мощная система для сбора, обработки и предоставления данных о манге из различных источников. Проект поддерживает парсинг с популярных платформ (MyAnimeList, Remanga, Shikimori), автоматический перевод с помощью OpenAI API, систему пользователей с персональными библиотеками и многое другое.

## ✨ Возможности
- 📚 **Парсинг данных** - Сбор информации с MAL, Remanga, Shikimori
- 🔄 **Автоматические обновления** - Регулярное обновление данных
- 🌐 **Мультиязычность** - Автоматический перевод описаний и названий через OpenAI API
- 👤 **Система пользователей** - Регистрация, аутентификация, OAuth (Google, Yandex)
- 📖 **Личные библиотеки** - Статусы чтения, закладки, прогресс чтения
- 🎨 **Обложки** - Автоматическое сохранение и оптимизация изображений
- 📧 **Email-уведомления** - Восстановление пароля и другие уведомления
- 🔍 **Продвинутый поиск** - Поиск по названиям, жанрам

## 🛠️ Технологии
- **Backend**: FastAPI, SQLModel, PostgreSQL, Redis
- **Парсинг**: AsyncIO, aiohttp, (прокси/апи ключи)-ротация
- **Перевод**: OpenAI API
- **Миграции**: Alembic
- **Кэширование**: Redis, fastapi-cache
- **Email**: SMTP с HTML-шаблонами

## 📋 Требования
- Python 3.10+
- PostgreSQL 13+
- Redis 6+

## 🚀 Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/xEncerx/shinga-api.git
cd shinga-api
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка окружения
Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

### 5. Применение миграций
```bash
alembic upgrade head
```

## ⚙️ Конфигурация

### Настройка прокси
Создайте файл `app/core/proxies.txt` и добавьте прокси в формате:
```
На данный момент поддерживаются только HTTP прокси

http://ip:port
http://username:password@ip:port
```

### Настройка OpenAI API
Создайте файл `app/core/openai_api_keys.txt` и добавьте API ключи:
```
sk-your-openai-key-1
sk-your-openai-key-2
```

## 🎯 Первоначальное заполнение данных
> **Важно**: Данный проект предоставляет инструменты для работы с данными, но не содержит готовых решений для парсинга конкретных источников. Пользователь должен самостоятельно реализовать логику получения данных в соответствии с правилами и условиями использования целевых ресурсов.

### Готовые утилиты для вашей реализации
В репозитории доступны следующие инструменты:
- **Proxy Manager** - ротация прокси-серверов
- **Api Key Manager** - ротация openai api ключей
- **Media Manager** - работа с обложками и медиа-файлами
- **Database CRUD** - операции с базой данных
- **OpenAI Integration** - автоматический перевод контента
- **Caching System** - кэширование результатов
- **Rate Limiting** - контроль частоты запросов

Изучите существующий код в `app/infrastructure/` и `app/providers/` для понимания архитектуры и создания собственных решений.

## 🔄 Автоматическое обновление

**Перед использованием заполните файлы с прокси/апи ключами openai**

Настройте количество воркеров **(num_workers)** в `updater.py`:

```python
async def main():
    # Настройте количество воркеров под ваши ресурсы
    async with GlobalTitlesUpdater(num_workers=7) as updater:
        await updater.idle()
```

После заполнения базы данных запустите систему автоматического обновления:

```bash
python updater.py
```

## 📧 Настройка Email

### Настройка SMTP
Настройте SMTP параметры в `.env`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Кастомизация шаблонов
Отредактируйте файлы в `templates/emails/`:

- `password_reset.html` - HTML шаблон для восстановления пароля
- `password_reset.txt` - Текстовый шаблон для восстановления пароля

## 🚀 Запуск
```bash
python main.py
```

## 📖 API Документация
После запуска приложения вам будет доступна документация по адресам:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Вклад в проект
1. Форкните проект
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add some amazing feature'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 🔗 Связанные проекты
### 📱 Shinga App
Приложение для чтения манги, использующее Shinga API

- **Репозиторий**: [shinga-app](https://github.com/xEncerx/shinga-app)
- **Платформы**: Android, Windows
- **Технологии**: Flutter

## 🆘 Поддержка
- **Email**: support@shinga.ru
- **Issues**: [GitHub Issues](https://github.com/xEncerx/shinga-api/issues)


<div align="center">
  <p><b>Shinga API</b> - создан с ❤️ для сообщества любителей манги</p>
</div>