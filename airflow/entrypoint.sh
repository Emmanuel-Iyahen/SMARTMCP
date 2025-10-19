#!/bin/bash
set -e

# Initialize DB (only first time)
airflow db migrate

# Create admin user if not exists
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com || true

# Start webserver + scheduler
airflow scheduler &
exec airflow webserver -p 8080
