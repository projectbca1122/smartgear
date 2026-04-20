# SmartGear Django Application

## Overview
A Django-based e-commerce application for SmartGear — a smart shopping platform with weather-based product recommendations powered by Google Gemini AI and OpenWeatherMap API.

## Architecture
- **Framework**: Django 4.2.7
- **Database**: SQLite3 (db.sqlite3)
- **Static Files**: WhiteNoise middleware for serving static files
- **AI**: Google Gemini API (gemini-2.5-flash) for AI assistant responses
- **Weather**: OpenWeatherMap API for weather-based product recommendations
- **Voice**: SpeechRecognition for voice input (server-side)

## Project Structure
```
sg/          - Django project configuration (settings, urls, wsgi)
core/        - Main application (models, views, urls, templates, admin)
staticfiles/ - Collected static files (served by WhiteNoise)
static/      - Source static files
db.sqlite3   - SQLite database
```

## Key Features
- Product catalog with weather-based recommendations
- User authentication with OTP support
- Shopping cart and wishlist
- Order management
- AI voice assistant powered by Gemini
- Weather integration via OpenWeatherMap

## Running the Application
- **Development**: `python manage.py runserver 0.0.0.0:5000`
- **Production**: `gunicorn --bind=0.0.0.0:5000 --reuse-port sg.wsgi:application`

## Configuration
- `ALLOWED_HOSTS = ['*']` — allows all hosts (required for Replit proxy)
- `CORS_ALLOWED_ALL_ORIGINS = True` — allows all CORS origins
- Gemini API key and Weather API key are hardcoded in `core/views.py`

## Notes
- pyttsx3 text-to-speech is lazily initialized to avoid server startup failures
- The `static/` directory must exist (created as empty if not present)
- Run `python manage.py collectstatic` after static file changes
