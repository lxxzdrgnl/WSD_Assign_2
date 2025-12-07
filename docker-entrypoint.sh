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

        echo "Loading seed data..."
        python3 scripts/seed_data.py 2>&1 || echo "Seed data failed, continuing..."
    else
        # If it's a different error, try to downgrade and upgrade
        echo "Attempting to reset migrations..."
        alembic downgrade base 2>/dev/null || true
        alembic upgrade head

        echo "Loading seed data..."
        python3 scripts/seed_data.py 2>&1 || echo "Seed data failed, continuing..."
    fi
else
    echo "Migrations completed successfully."

    # Check if seed data already exists
    echo "Checking if seed data needs to be loaded..."
    set +e  # Temporarily disable exit on error
    python3 << EOF
import pymysql
import os

try:
    conn = pymysql.connect(
        host='db',
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME']
    )
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count == 0:
            print("No users found, will load seed data")
            exit(1)
        else:
            print(f"Found {count} users, skipping seed data")
            exit(0)
    conn.close()
except Exception as e:
    print(f"Error checking users: {e}, will load seed data")
    exit(1)
EOF
    NEED_SEED=$?
    set -e  # Re-enable exit on error

    if [ $NEED_SEED -ne 0 ]; then
        echo "Loading seed data..."
        if python3 scripts/seed_data.py 2>&1; then
            echo "Seed data loaded successfully"
        else
            echo "Failed to load seed data, error code: $?"
            echo "Continuing anyway..."
        fi
    fi
fi

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
