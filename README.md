# Medical Book Validation Service

Сервис для валидации электронных личных медицинских книжек (ЭЛМК) с интеграцией к внешнему API Роспотребнадзора.

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)

### Запуск с Docker

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd elmk-integration-service-main
```

2. **Создайте файл .env:**
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

3. **Запустите сервис:**
```bash
# С Docker Compose
docker-compose up

# Или с Docker напрямую
docker build -t medical-book-service .
docker run -p 8000:8000 --env-file .env medical-book-service
```

4. **Проверьте работу сервиса:**
```bash
curl http://localhost:8000/healthz
```

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
    "first_name": "Ху***ул",
    "last_name": "О***",
    "middle_name": "Абд***вна",
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

## ⚙️ Конфигурация

Все настройки через переменные окружения:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `AUTH_USERNAME` | Имя пользователя Basic Auth | - |
| `AUTH_PASSWORD` | Пароль Basic Auth | - |
| `EXTERNAL_API_URL` | URL внешнего API | `https://elmk.rospotrebnadzor.ru/api/gov-services/elmks/public_elmk` |
| `EXTERNAL_API_TIMEOUT` | Таймаут внешнего API (сек) | `30` |
| `RATE_LIMIT_REQUESTS` | Лимит запросов | `100` |
| `RATE_LIMIT_WINDOW` | Окно лимита (сек) | `3600` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `SECRET_KEY` | Секретный ключ | `your-secret-key-here` |

## ✅ Валидация данных

### ELMK Number
- Формат: ровно 12 цифр
- Регулярное выражение: `^\d{12}$`
- Автоматическое форматирование: `860102797025` → `86-01-027970-25`

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

# С подробным выводом
pytest -v

# Только API тесты
pytest tests/test_api.py -v
```

### Ручное тестирование

```bash
# Тест health check
curl http://localhost:8000/healthz

# Тест валидации (с аутентификацией)
curl -X POST http://localhost:8000/api/v1/medical-book/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46c2VjdXJlcGFzc3dvcmQxMjM=" \
  -d '{"elmk_number": "860102797025", "snils": "17648922116"}'
```

## 🐳 Docker

### Сборка образа

```bash
docker build -t medical-book-service .
```

### Запуск контейнера

```bash
docker run -p 8000:8000 --env-file .env medical-book-service
```

### Docker Compose

```bash
docker-compose up -d
```

## 🔧 Разработка

### Локальная разработка

1. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

2. **Запустите сервис:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. **Запустите тесты:**
```bash
pytest -v
```

### Структура проекта

```
elmk-integration-service-main/
├── app/
│   ├── __init__.py
│   ├── api.py          # API endpoints
│   ├── auth.py         # Аутентификация
│   ├── config.py       # Конфигурация
│   ├── external_api.py # Интеграция с внешним API
│   ├── main.py         # Основное приложение
│   ├── middleware.py   # Middleware
│   └── models.py       # Pydantic модели
├── tests/
│   ├── __init__.py
│   ├── test_api.py     # API тесты
│   └── test_models.py  # Модели тесты
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

## 🚨 Известные проблемы и решения

### SSL проблемы с внешним API

Сервис использует curl с отключенной SSL верификацией для обхода проблем с устаревшими SSL протоколами внешнего API.

### Форматирование ELMK номера

Сервис автоматически форматирует ELMK номер из 12-значного формата в формат с дефисами для совместимости с внешним API.

## 📝 Лицензия

MIT License

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

При возникновении проблем создайте issue в репозитории или обратитесь к команде разработки.
