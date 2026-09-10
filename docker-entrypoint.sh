#!/bin/sh
set -e

python scripts/wait_for_service.py "${POSTGRES_HOST:-db}" "${POSTGRES_PORT:-5432}" "PostgreSQL"

if [ -n "$REDIS_URL" ]; then
  python scripts/wait_for_service.py redis 6379 Redis
fi

python manage.py migrate --noinput
python manage.py setup_groups
python manage.py collectstatic --noinput

exec "$@"
