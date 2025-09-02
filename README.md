[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)
[![Русский](https://img.shields.io/badge/lang-Русский-red.svg)](README.ru.md)

# 🍃 Shinga API
**Your manga world** - REST API for parsing, storing, and managing manga

Shinga API is a powerful system for collecting, processing, and providing manga data from various sources. The project supports parsing from popular platforms (MyAnimeList, Remanga, Shikimori), automatic translation using OpenAI API, user system with personal libraries, and much more.

## ✨ Features
- 📚 **Data parsing** - Collecting information from MAL, Remanga, Shikimori
- 🔄 **Automatic updates** - Regular data updates
- 🌐 **Multilingual support** - Automatic translation of descriptions and titles via OpenAI API
- 👤 **User system** - Registration, authentication, OAuth (Google, Yandex)
- 📖 **Personal libraries** - Reading statuses, bookmarks, reading progress
- 🎨 **Cover images** - Automatic saving and optimization of images
- 📧 **Email notifications** - Password recovery and other notifications
- 🔍 **Advanced search** - Search by titles, genres

## 🛠️ Technologies
- **Backend**: FastAPI, SQLModel, PostgreSQL, Redis
- **Parsing**: AsyncIO, aiohttp, (proxy/API keys) rotation
- **Translation**: OpenAI API
- **Migrations**: Alembic
- **Caching**: Redis, fastapi-cache
- **Email**: SMTP with HTML templates

## 📋 Requirements
- Python 3.10+
- PostgreSQL 13+
- Redis 6+

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/xEncerx/shinga-api.git
cd shinga-api
```

### 2. Create virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment setup
Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

### 5. Apply migrations
```bash
alembic upgrade head
```

## ⚙️ Configuration
### Proxy setup (OPTIONAL)
> Proxies are used to avoid flood errors when parsing titles or downloading covers. If proxies are not configured, parsing occurs with 2 workers.

Create a file `app/core/proxies.txt` and add proxies in the format:
```
Currently only HTTP proxies are supported

http://ip:port
http://username:password@ip:port
```

### OpenAI API setup (OPTIONAL)
> Translation is temporarily removed from the project

Create a file `app/core/openai_api_keys.txt` and add API keys:
```
sk-your-openai-key-1
sk-your-openai-key-2
```

### 📧 Email notifications setup (SMTP)
Configure SMTP parameters in `.env`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```
### Template customization
Edit files in `templates/emails/`:

- `password_reset.html` - HTML template for password recovery
- `password_reset.txt` - Text template for password recovery

## 🎯 Data population and subsequent updates
### 🚨 Important warning
> **Warning:** This tool is intended for **personal, non-commercial use**. Use it responsibly.
>
> - **Do not use** aggressive mode with many proxies to bypass limitations;
> - **Respect** rate limits of target websites;
> - Website administrators may **block your IP address** if they suspect parsing;
> - The project author **is not responsible** for consequences of improper use of this code;
>
> **Use at your own risk.**

After filling in the configs and proxies, run the `updater.py` file:
```bash
python updater.py
```
This will start collecting titles into your Database. It will update the data to current information at regular intervals.

## 🚀 Running the REST API
```bash
python main.py
```

## 📖 API Documentation
After starting the application, documentation will be available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 Related projects
### 📱 Shinga App
Manga reading application using Shinga API

- **Repository**: [shinga-app](https://github.com/xEncerx/shinga-app)
- **Platforms**: Android, Windows
- **Technologies**: Flutter

## 🆘 Support
- **Email**: support@shinga.ru
- **Issues**: [GitHub Issues](https://github.com/xEncerx/shinga-api/issues)


<div align="center">
  <p><b>Shinga API</b> - created with ❤️ for the manga lovers community</p>
</div>