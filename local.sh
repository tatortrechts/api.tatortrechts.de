#!/usr/bin/env bash

# To run form scratch:
# ./local.sh --build --no-cache

docker-compose up --remove-orphans "$@"
