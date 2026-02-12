#!/bin/bash
set -e

mkdir -p /var/www/shinga/storage/covers
mkdir -p /var/www/shinga/storage/avatars

echo "Starting application..."
exec "$@"