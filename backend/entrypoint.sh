#!/bin/bash

# Wait for Neo4j to be ready
echo "Waiting for Neo4j to be available..."
until nc -z neo4j 7687; do
    echo "Neo4j is not ready yet - sleeping"
    sleep 2
done
echo "Neo4j is up - executing migration"

# Run migration script
python /app/main_migration.py

# Check migration exit code
if [ $? -eq 0 ]; then
    echo "Migration completed successfully, starting FastAPI app..."
else
    echo "Migration failed, exiting..."
    exit 1
fi

# Start FastAPI app
exec "$@"