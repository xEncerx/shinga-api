[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)
[![Русский](https://img.shields.io/badge/lang-Русский-red.svg)](README.ru.md)

# 🍃 Shinga API
**Your manga world** - REST API for parsing, storing and managing manga

Shinga API is a powerful system for collecting, processing and providing manga data from various sources. The project supports parsing from popular platforms (MyAnimeList, Remanga, Shikimori), automatic translation using OpenAI API, user system with personal libraries and much more.

## ✨ Features
- 📚 **Data parsing** - Collecting information from MAL, Remanga, Shikimori
- 🔄 **Automatic updates** - Regular data updates
- 🌐 **Multilingual** - Automatic translation of descriptions and titles via OpenAI API
- 👤 **User system** - Registration, authentication, OAuth (Google, Yandex)
- 📖 **Personal libraries** - Reading statuses, bookmarks, reading progress
- 🎨 **Covers** - Automatic saving and optimization of images
- 📧 **Email notifications** - Password recovery and other notifications
- 🔍 **Advanced search** - Search by titles, genres

## 🛠️ Technologies
- **Backend**: FastAPI, SQLModel, PostgreSQL, Redis
- **Parsing**: AsyncIO, aiohttp, (proxy/api keys)-rotation
- **Translation**: OpenAI API
- **Migrations**: Alembic
- **Caching**: Redis, fastapi-cache
- **Email**: SMTP with HTML templates

## 📋 Requirements
- Python 3.10+
- PostgreSQL 13+
- Redis 6+

## 🚀 Installation

### 1. Clone repository
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
Create `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

### 5. Apply migrations
```bash
alembic upgrade head
```

## ⚙️ Configuration

### Proxy setup
Create file `app/core/proxies.txt` and add proxies in format:
```
Currently only HTTP proxies are supported

http://ip:port
http://username:password@ip:port
```

### OpenAI API setup
Create file `app/core/openai_api_keys.txt` and add API keys:
```
sk-your-openai-key-1
sk-your-openai-key-2
```

## 🎯 Initial data population
> **Important**: This project provides tools for working with data, but does not contain ready-made solutions for parsing specific sources. The user must implement the data retrieval logic themselves in accordance with the rules and terms of use of the target resources.

### Ready-made utilities for your implementation
The following tools are available in the repository:
- **Proxy Manager** - proxy server rotation
- **Api Key Manager** - OpenAI API key rotation
- **Media Manager** - working with covers and media files
- **Database CRUD** - database operations
- **OpenAI Integration** - automatic content translation
- **Caching System** - result caching
- **Rate Limiting** - request frequency control

Study the existing code in `app/infrastructure/` and `app/providers/` to understand the architecture and create your own solutions.

## 🔄 Automatic updates

**Before using, fill in the files with proxies/OpenAI API keys**

Configure the number of workers **(num_workers)** in `updater.py`:

```python
async def main():
    # Configure the number of workers for your resources
    async with GlobalTitlesUpdater(num_workers=7) as updater:
        await updater.idle()
```

After filling the database, run the automatic update system:

```bash
python updater.py
```

## 📧 Email setup

### SMTP setup
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

## 🚀 Launch
```bash
python main.py
```

## 📖 API Documentation
After launching the application, documentation will be available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing
1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

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