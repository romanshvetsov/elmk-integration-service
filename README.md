# Medical Book Validation Service

Сервис для валидации электронных личных медицинских книжек с использованием внешнего API Роспотребнадзора.

## 🚀 Быстрый старт

### Локальная установка

```bash
# Клонирование и установка зависимостей
git clone <repository-url>
cd medical-book-service
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Настройка конфигурации
cp .env.example .env
# Отредактируйте .env файл с вашими настройками

# Запуск сервиса
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker

```bash
# Сборка и запуск
docker build -t medical-book-service .
docker run -p 8000:8000 --env-file .env medical-book-service

# Или с Docker Compose
docker-compose up -d
```

## 📋 Требования

- Python 3.11+
- Docker (опционально)

## 🏗️ Архитектура

- **FastAPI** - современный веб-фреймворк для Python
- **Pydantic** - валидация данных и сериализация
- **HTTPX** - асинхронные HTTP-клиенты
- **Structlog** - структурированное логирование
- **Docker** - контейнеризация

## 🔧 Конфигурация

Все настройки через переменные окружения:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `AUTH_USERNAME` | Имя пользователя Basic Auth | - |
| `AUTH_PASSWORD` | Пароль Basic Auth | - |
| `EXTERNAL_API_URL` | URL внешнего API | `https://elmk.rospotrebnadzor.ru/registry` |
| `EXTERNAL_API_TIMEOUT` | Таймаут внешнего API (сек) | `30` |
| `RATE_LIMIT_REQUESTS` | Лимит запросов | `100` |
| `RATE_LIMIT_WINDOW` | Окно лимита (сек) | `3600` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `SECRET_KEY` | Секретный ключ | - |

## 📚 API Endpoints

### POST /api/v1/medical-book/validate

Валидация медицинской книжки.

**Аутентификация:** Basic Auth

**Request Body:**
```json
{
    "elmk_number": "860102797025",
    "snils": "17648922116"
}
```

**Response:**
```json
{
    "elmk_status_name": "Действует",
    "elmk_number": "86-01-027970-25",
    "first_name": "Хуснигул",
    "last_name": "О***",
    "middle_name": "Абдусатторовна",
    "snils": "176***16",
    "work_type": [
        "Работы, при выполнении которых осуществляется контакт с пищевыми продуктами в процессе их производства, хранения, транспортировки и реализации"
    ],
    "decision_dt": "2025-07-11T07:52:57Z",
    "med_opinions_dt": "2026-07-02",
    "certification_dt": "2025-07-11",
    "recertification_dt": "2026-07-11",
    "fbuz_short_name": "ФБУЗ «ЦГиЭ в ХМАО-Югре»",
    "created_fullname": "ЕПГУ"
}
```

### GET /healthz

Проверка состояния сервиса.

### GET /metrics

Метрики сервиса (заглушка для Prometheus).

## ✅ Валидация данных

### ELMK Number
- Формат: ровно 12 цифр
- Регулярное выражение: `^\d{12}$`

### SNILS
- Формат: ровно 11 цифр
- Регулярное выражение: `^\d{11}$`

## 🔒 Безопасность

- **Basic Auth** - аутентификация пользователей
- **Rate Limiting** - ограничение частоты запросов
- **Валидация входных данных** - строгая проверка форматов
- **HTTPS** - обязательное использование в продакшене
- **Логирование** - запись всех событий безопасности

## 📊 Логирование

Сервис использует структурированное логирование в формате JSON:

```json
{
    "timestamp": "2025-08-03T13:42:22.024532Z",
    "level": "info",
    "event": "Request started",
    "method": "POST",
    "url": "/api/v1/medical-book/validate",
    "client_ip": "127.0.0.1"
}
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=app --cov-report=html

# Конкретный тест
pytest tests/test_api.py::TestHealthCheck::test_health_check
```

### Тестовый скрипт

```bash
python test_api.py
```

## 📖 Документация

- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker

### Сборка образа

```bash
docker build -t medical-book-service .
```

### Запуск контейнера

```bash
docker run -d \
  --name medical-book-service \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  medical-book-service
```

### Docker Compose

```bash
docker-compose up -d
```

## 📈 Мониторинг

- **Health Check**: `/healthz`
- **Metrics**: `/metrics` (заглушка)
- **Documentation**: `/docs` (Swagger UI)

## 🚀 Развертывание

### Production

1. Настройте HTTPS (nginx + SSL)
2. Измените секретные ключи в `.env`
3. Настройте мониторинг
4. Настройте логирование в файл/систему

### Docker Production

```bash
docker run -d \
  --name medical-book-service \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  medical-book-service
```

## 📁 Структура проекта

```
medical-book-service/
├── app/                    # Основной код приложения
│   ├── __init__.py
│   ├── main.py            # Точка входа FastAPI
│   ├── api.py             # API эндпоинты
│   ├── models.py          # Pydantic модели
│   ├── config.py          # Конфигурация
│   ├── auth.py            # Аутентификация
│   ├── external_api.py    # Клиент внешнего API
│   └── middleware.py      # Middleware
├── tests/                 # Тесты
│   ├── __init__.py
│   ├── test_api.py        # API тесты
│   └── test_models.py     # Модели тесты
├── requirements.txt        # Зависимости Python
├── Dockerfile             # Docker образ
├── docker-compose.yml     # Docker Compose
├── .env.example          # Пример конфигурации
├── .gitignore            # Git ignore
├── pytest.ini           # Конфигурация pytest
├── README.md             # Документация
├── API_DOCUMENTATION.md  # API документация
└── test_api.py           # Тестовый скрипт
```

## 🔧 Разработка

### Установка зависимостей для разработки

```bash
pip install -r requirements.txt
```

### Запуск в режиме разработки

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Линтинг и форматирование

```bash
# Установка дополнительных инструментов
pip install black isort flake8

# Форматирование кода
black app/ tests/
isort app/ tests/

# Проверка стиля
flake8 app/ tests/
```

## 📝 Лицензия

MIT License

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи сервиса
2. Убедитесь, что все переменные окружения настроены
3. Проверьте доступность внешнего API
4. Создайте issue в репозитории