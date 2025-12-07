#!/bin/bash
set -e

echo "Waiting for database to be ready..."
sleep 5

echo "Running database migrations..."

# Try to run migrations
if ! alembic upgrade head 2>/dev/null; then
    echo "Migration failed, checking if it's a revision mismatch..."

    # Check if it's a revision error
    if alembic current 2>&1 | grep -q "Can't locate revision"; then
        echo "Detected revision mismatch. Clearing alembic version table..."

        # Drop and recreate database using Python and pymysql
        python3 << EOF
import pymysql
import os

try:
    # Connect without specifying database
    conn = pymysql.connect(
        host='db',
        user='root',
        password=os.environ['DB_ROOT_PASSWORD']
    )
    with conn.cursor() as cursor:
        # Drop and recreate database
        cursor.execute(f"DROP DATABASE IF EXISTS {os.environ['DB_NAME']}")
        cursor.execute(f"CREATE DATABASE {os.environ['DB_NAME']}")
    conn.commit()
    conn.close()
    print("Database recreated successfully.")
except Exception as e:
    print(f"Warning: Could not recreate database: {e}")
EOF

        echo "Running migrations from scratch..."
        alembic upgrade head
    else
        # If it's a different error, try to downgrade and upgrade
        echo "Attempting to reset migrations..."
        alembic downgrade base 2>/dev/null || true
        alembic upgrade head
    fi
fi

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
