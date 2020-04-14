#!/bin/bash

if [ "$1" = "flask" ]; then
  source ./scripts/server/run_flask.sh
elif [ "$1" = "gunicorn" ]; then
  source ./scripts/server/run_gunicorn.sh
elif [ "$1" = "nginx" ]; then
  source ./scripts/server/run_nginx.sh
else
  echo "Invalid server name"
fi
