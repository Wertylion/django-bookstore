#!/bin/sh
set -e

FIXTURE_PATH="${1:-/tmp/bookstore-data.json}"

if [ ! -f "db.sqlite3" ]; then
  echo "db.sqlite3 not found. Run this script from the Django project directory."
  exit 1
fi

echo "Exporting SQLite data to ${FIXTURE_PATH}"
DB_ENGINE=sqlite ../.venv/bin/python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --indent 2 \
  > "${FIXTURE_PATH}"

echo "Start PostgreSQL services:"
echo "  docker compose up -d db redis"
echo
echo "Then import into PostgreSQL:"
echo "  docker compose run --rm -v ${FIXTURE_PATH}:${FIXTURE_PATH} web python manage.py loaddata ${FIXTURE_PATH}"
