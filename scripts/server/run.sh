#!/bin/bash

if [ "$1" = "flask" ]; then
  ./scripts/server/run_flask.sh
elif [ "$1" = "gunicorn" ]; then
  ./scripts/server/run_gunicorn.sh
elif [ "$1" = "nginx" ]; then
  ./scripts/server/run_nginx.sh
else
  echo "Invalid server name"
fi
