# sosandex-hospital — Микросервис городской больницы

RESTful-микросервис на **FastAPI** с реляционной СУБД **PostgreSQL**, развёрнутый в Docker (multi-stage сборка) через docker-compose.

## Возможности

- 19 REST-эндпоинтов: врачи, пациенты, приёмы (записи), расписание, страницы UI
- Реляционная СУБД PostgreSQL (в контейнере), локально для разработки — SQLite
- Обработка ошибок: 404 (сущность не найдена), 422 (невалидные данные, Pydantic), сервис не падает при некорректном запросе
- Автоматическое создание таблиц при старте (init_db)

## Запуск (Docker)

```bash
docker compose up --build -d
```

Сервис: http://localhost:8000
Swagger UI (документация API): http://localhost:8000/docs

### Сервисы docker-compose

| Сервис | Образ | Порт | Назначение |
|---|---|---|---|
| `app` | сборка из Dockerfile | 8000 | микросервис FastAPI |
| `db` | postgres:16-alpine | 5432 (внутр.) | реляционная СУБД PostgreSQL |
| `pgadmin` | dpage/pgadmin4 | **8084** | веб-интерфейс управления СУБД |

### pgAdmin

Веб-интерфейс для работы с базой данных: **http://localhost:8084**

Учётные данные (задаются в docker-compose):

- логин: `admin@example.com`
- пароль: `lab12-admin`

После входа → **Add New Server**:

- вкладка **Connection**: Host = `db`, Port = `5432`, Maintenance database = `hospital`, User = `hospital`, Password = `hospital`.

Остановка:

```bash
docker compose down          # данные PostgreSQL сохраняются в volume pgdata
docker compose down -v       # вместе с данными
```

## Структура

```
app/
├── main.py                 # точка входа (FastAPI + lifespan/init_db)
├── database.py             # URL БД из env (DATABASE_URL), сессии, init_db
├── models/
│   ├── database_models.py  # SQLAlchemy-модели (doctors, patients, appointments, schedule_slots)
│   └── schemas.py          # Pydantic-схемы (валидация входящих данных)
├── routers/
│   ├── doctors.py          # CRUD врачей + слоты расписания
│   ├── patients.py         # CRUD пациентов
│   ├── appointments.py     # CRUD записей на приём
│   └── pages.py            # HTML-страницы (Jinja2)
├── services/
├── templates/  static/
tests/                      # pytest (in-memory SQLite)
Dockerfile                  # multi-stage: builder (venv) → runtime
docker-compose.yml          # app + PostgreSQL
```

## Проверка (Postman / curl)

### Врачи

| Метод | URL | Тело (JSON) |
|---|---|---|
| GET | `/api/doctors/` | — |
| GET | `/api/doctors/{id}` | — |
| POST | `/api/doctors/` | `{"first_name":"Иван","last_name":"Петров","specialty":"Хирург","cabinet":"101"}` |
| PUT | `/api/doctors/{id}` | то же |
| DELETE | `/api/doctors/{id}` | — |

### Пациенты

| Метод | URL | Тело |
|---|---|---|
| GET | `/api/patients/` | — |
| POST | `/api/patients/` | `{"first_name":"Анна","last_name":"Сидорова","phone":"+79001234567"}` |
| DELETE | `/api/patients/{id}` | — |

### Приёмы

| Метод | URL | Тело |
|---|---|---|
| GET | `/api/appointments/` | — |
| POST | `/api/appointments/` | `{"patient_id":1,"doctor_id":1,"appointment_date":"2026-11-20","start_time":"10:00","end_time":"10:30"}` |

### Примеры проверки ошибок (curl)

```bash
# 404 — несуществующий врач
curl -i http://localhost:8000/api/doctors/999999

# 422 — некорректные данные (нет обязательных полей)
curl -i -X POST http://localhost:8000/api/doctors/ \
     -H 'Content-Type: application/json' -d '{"first_name":"x"}'
```

## Локальная разработка (без Docker)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000   # используется SQLite hospital.db
make test   # pytest (in-memory SQLite)
```

## Конфигурация

| Переменная | Назначение | По умолчанию |
|---|---|---|
| `DATABASE_URL` | URL СУБД (SQLAlchemy) | `sqlite+aiosqlite:///./hospital.db` |

В docker-compose задаётся `postgresql+asyncpg://hospital:hospital@db:5432/hospital`.
