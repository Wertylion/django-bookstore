# Book Store

[![Django CI](https://github.com/Wertylion/django-bookstore/actions/workflows/django.yml/badge.svg)](https://github.com/Wertylion/django-bookstore/actions/workflows/django.yml)
![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)

Django learning project for a bookstore with catalog pages, authentication, cart, orders, Stripe Checkout, Docker, i18n and tests.

## Setup

```bash
python -m venv ../.venv
../.venv/bin/python -m pip install -r requirements.txt
../.venv/bin/python manage.py migrate
../.venv/bin/python manage.py setup_groups
```

## Run Locally

```bash
../.venv/bin/python manage.py runserver 127.0.0.1:8000
```

Main pages:

- `/books/`
- `/order/cart/`
- `/register/`
- `/login/`
- `/async/summary/`
- `/async/books/`

## Docker

```bash
docker compose up --build
```

The compose stack contains Django, PostgreSQL and Redis with healthchecks and volumes.

Production-style stack for the last backend homework:

- `web`: Gunicorn + Django
- `nginx`: reverse proxy and static/media file serving
- `db`: PostgreSQL
- `redis`: cache, Celery broker and result backend
- `celery`: background worker
- `celery-beat`: periodic task scheduler

The Django app exposes `/health/` for Docker, nginx and cloud load balancer checks.

Production containers use `config.settings_production`, Gunicorn and WhiteNoise. Set these values in the deployment environment:

```env
DJANGO_SETTINGS_MODULE=config.settings_production
DJANGO_SETTINGS_ENV=production
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=replace-with-a-strong-secret
DJANGO_ALLOWED_HOSTS=your-domain.com,.railway.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com
DB_ENGINE=postgresql
POSTGRES_DB=bookstore
POSTGRES_USER=bookstore
POSTGRES_PASSWORD=replace-with-a-strong-password
POSTGRES_HOST=your-postgres-host
POSTGRES_PORT=5432
REDIS_URL=redis://your-redis-host:6379/1
```

For Railway/Render/Heroku-style platforms, run the web process with:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

GitHub Actions workflow `.github/workflows/django.yml` runs flake8, black, pytest with coverage, builds the Docker image, and pushes to Docker Hub on `push` when `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository secrets are configured.

Sentry can be enabled with:

```env
SENTRY_DSN=https://...
```

Celery tasks:

- `order.tasks.send_order_created_email`
- `shop.tasks.generate_catalog_report`
- `order.tasks.clear_expired_sessions`

## Environment

Copy `.env.example` to `.env` and update values if needed.

Stripe test payments need:

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

Without a Stripe key, checkout falls back to the order success page.

## Internationalization

The project supports Ukrainian and English.

```bash
../.venv/bin/python manage.py makemessages -l uk -l en
../.venv/bin/python manage.py compilemessages
```

The language selector is in the navbar and uses Django's `/i18n/setlang/` endpoint.

## Tests

```bash
../.venv/bin/pytest
```

Coverage:

```bash
../.venv/bin/coverage run -m pytest
../.venv/bin/coverage report
```

Current coverage after the AI testing homework: 91%.

## REST API

API documentation:

- `/api/docs/`
- `/api/schema/`

JWT authentication:

- `POST /api/token/`
- `POST /api/token/refresh/`
- `POST /api/token/verify/`

Main API resources:

- `/api/books/`
- `/api/categories/`
- `/api/orders/`
- `/api/cart/`
- `/api/cart/add/`
- `/api/cart/remove/`
- `/api/cart/clear/`

The API uses DRF ViewSets with routers, nested serializers, pagination, filtering, throttling, JWT authentication and CORS.

## AI Usage

AI was used for:

- Reviewing `BookListView`, `NewOrderView` and `CreateCheckoutSessionView`.
- Identifying safe improvements: price validation, earlier empty-cart validation, docstrings and mock-based Stripe tests.
- Generating pytest-django test drafts for models, forms, views, cart, checkout, Stripe and i18n.
- Generating documentation drafts for view docstrings and README content.

All AI output was reviewed and modified before being committed to the project.
