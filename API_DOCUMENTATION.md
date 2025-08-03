# API Documentation

## Обзор

Medical Book Validation Service предоставляет REST API для валидации электронных личных медицинских книжек с использованием внешнего API Роспотребнадзора.

## Базовый URL

```
http://localhost:8000
```

## Аутентификация

Все API эндпоинты (кроме `/healthz` и `/metrics`) требуют Basic Authentication.

### Формат заголовка

```
Authorization: Basic <base64(username:password)>
```

### Пример

```bash
# Кодирование учетных данных
echo -n "admin:secure_password_here" | base64
# Результат: YWRtaW46c2VjdXJlX3Bhc3N3b3JkX2hlcmU=

# Использование в запросе
curl -H "Authorization: Basic YWRtaW46c2VjdXJlX3Bhc3N3b3JkX2hlcmU=" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/api/v1/medical-book/validate \
     -d '{"elmk_number": "860102797025", "snils": "17648922116"}'
```

## Эндпоинты

### 1. Health Check

**GET** `/healthz`

Проверка состояния сервиса.

#### Запрос

```bash
curl http://localhost:8000/healthz
```

#### Ответ

```json
{
  "status": "healthy",
  "timestamp": "2025-08-03T13:42:22.024532Z",
  "version": "1.0.0"
}
```

### 2. Валидация медицинской книжки

**POST** `/api/v1/medical-book/validate`

Валидация медицинской книжки по номеру ЭЛМК и СНИЛС.

#### Запрос

```bash
curl -X POST http://localhost:8000/api/v1/medical-book/validate \
     -H "Authorization: Basic YWRtaW46c2VjdXJlX3Bhc3N3b3JkX2hlcmU=" \
     -H "Content-Type: application/json" \
     -d '{
       "elmk_number": "860102797025",
       "snils": "17648922116"
     }'
```

#### Тело запроса

```json
{
  "elmk_number": "860102797025",
  "snils": "17648922116"
}
```

#### Параметры

| Параметр | Тип | Обязательный | Описание | Валидация |
|----------|-----|--------------|----------|-----------|
| `elmk_number` | string | Да | Номер электронной личной медицинской книжки | Ровно 12 цифр |
| `snils` | string | Да | Номер СНИЛС | Ровно 11 цифр |

#### Успешный ответ (200)

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

#### Ошибки валидации (422)

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "elmk_number"],
      "msg": "Value error, ELMK number must be exactly 12 digits",
      "input": "12345678901",
      "ctx": {"error": {}}
    }
  ]
}
```

#### Ошибка аутентификации (401)

```json
{
  "detail": "Not authenticated"
}
```

#### Ошибка внешнего API (502/503/504)

```json
{
  "detail": "External API error: 500"
}
```

### 3. Метрики

**GET** `/metrics`

Получение метрик сервиса (заглушка для Prometheus).

#### Запрос

```bash
curl http://localhost:8000/metrics
```

#### Ответ

```json
{
  "status": "metrics endpoint",
  "note": "Prometheus metrics would be implemented here"
}
```

## Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 401 | Не авторизован |
| 404 | Медицинская книжка не найдена |
| 422 | Ошибка валидации данных |
| 429 | Превышен лимит запросов |
| 500 | Внутренняя ошибка сервера |
| 502 | Ошибка внешнего API |
| 503 | Внешний API недоступен |
| 504 | Таймаут внешнего API |

## Валидация данных

### ELMK Number
- **Формат**: Ровно 12 цифр
- **Регулярное выражение**: `^\d{12}$`
- **Пример**: `860102797025`

### SNILS
- **Формат**: Ровно 11 цифр
- **Регулярное выражение**: `^\d{11}$`
- **Пример**: `17648922116`

## Rate Limiting

Сервис ограничивает количество запросов:
- **Лимит**: 100 запросов в час на IP-адрес
- **При превышении**: HTTP 429 с описанием ошибки

## Логирование

Все запросы и ошибки логируются в структурированном формате JSON:

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

## Примеры использования

### Python

```python
import requests
import base64

# Настройки
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "secure_password_here"

# Кодирование учетных данных
credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()

# Заголовки
headers = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/json"
}

# Данные для валидации
data = {
    "elmk_number": "860102797025",
    "snils": "17648922116"
}

# Запрос
response = requests.post(
    f"{BASE_URL}/api/v1/medical-book/validate",
    json=data,
    headers=headers
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Medical book status: {result['elmk_status_name']}")
    print(f"Name: {result['first_name']} {result['last_name']}")
else:
    print(f"Error: {response.text}")
```

### JavaScript

```javascript
const BASE_URL = 'http://localhost:8000';
const USERNAME = 'admin';
const PASSWORD = 'secure_password_here';

// Кодирование учетных данных
const credentials = btoa(`${USERNAME}:${PASSWORD}`);

// Данные для валидации
const data = {
    elmk_number: "860102797025",
    snils: "17648922116"
};

// Запрос
fetch(`${BASE_URL}/api/v1/medical-book/validate`, {
    method: 'POST',
    headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => {
    console.log('Medical book status:', data.elmk_status_name);
    console.log('Name:', `${data.first_name} ${data.last_name}`);
})
.catch(error => console.error('Error:', error));
```

### cURL

```bash
# Health check
curl http://localhost:8000/healthz

# Валидация медицинской книжки
curl -X POST http://localhost:8000/api/v1/medical-book/validate \
     -H "Authorization: Basic YWRtaW46c2VjdXJlX3Bhc3N3b3JkX2hlcmU=" \
     -H "Content-Type: application/json" \
     -d '{
       "elmk_number": "860102797025",
       "snils": "17648922116"
     }'

# Тест с невалидными данными
curl -X POST http://localhost:8000/api/v1/medical-book/validate \
     -H "Authorization: Basic YWRtaW46c2VjdXJlX3Bhc3N3b3JkX2hlcmU=" \
     -H "Content-Type: application/json" \
     -d '{
       "elmk_number": "12345678901",
       "snils": "17648922116"
     }'
```

## Безопасность

- **HTTPS**: Обязательно в продакшене
- **Basic Auth**: Защита всех эндпоинтов
- **Валидация**: Строгая проверка входных данных
- **Rate Limiting**: Защита от DDoS
- **Логирование**: Запись всех событий безопасности

## Мониторинг

- **Health Check**: `/healthz`
- **Метрики**: `/metrics`
- **Документация**: `/docs` (Swagger UI)
- **ReDoc**: `/redoc`