# Локальный запуск

Для запуска нужны Docker и виртуальное окружение Python `3.12` в каталоге `.venv` с установленными зависимостями из `requirements.txt`.
Команды выполняются из корневого каталога проекта.

```bash
docker run -d \
  --name ecommerce-postgres \
  -e POSTGRES_USER=ecommerce_user \
  -e POSTGRES_PASSWORD=local_dev_password \
  -e POSTGRES_DB=ecommerce_db \
  -p 127.0.0.1:5432:5432 \
  -v ecommerce-postgres-18-data:/var/lib/postgresql \
  postgres:18.7
```

Логин, пароль и имя базы данных уже указаны в `app/database.py` и `alembic.ini`.
`Volume` обеспечивает сохранность данных базы при пересоздании контейнера.

Применение миграций:

```bash
alembic upgrade head
```

Запуск приложения:

```bash
uvicorn app.main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs
