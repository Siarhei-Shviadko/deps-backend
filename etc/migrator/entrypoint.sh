#!/usr/bin/env bash

if [ -z "$DATABASE_HOST" ] || [ -z "$DATABASE_PORT" ] || [ -z "$DATABASE_DB" ] || [ -z "$DATABASE_USER" ] || [ -z "$DATABASE_PASSWORD" ]; then
    echo "Please, specify DB credentials DATABASE_HOST DATABASE_PORT DATABASE_DB DATABASE_USER DATABASE_PASSWORD"
    exit 1;
fi

LIQUIBASE_URL="jdbc:postgresql://$DATABASE_HOST:$DATABASE_PORT/$DATABASE_DB"

exec ./wait-for.sh $DATABASE_HOST:$DATABASE_PORT -- echo "N" | /liquibase/liquibase \
    --driver="org.postgresql.Driver" \
    --changeLogFile="$MASTER_CHANGELOG" \
    --logLevel="warning" \
    --url="$LIQUIBASE_URL" \
    --username="$DATABASE_USER" \
    --password="$DATABASE_PASSWORD" \
    "$@"

