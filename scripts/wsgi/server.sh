#!/bin/bash

if [ "$1" = "flask" ]; then
  flask run --host=localhost --port 8000
elif [ "$1" = "gunicorn" ]; then
  gunicorn --config ./src/configs/gunicorn.py wsgi:app
elif [ "$1" = "nginx" ]; then
  sudo nginx -p $PWD -c $PWD/src/configs/nginx.conf
else
  echo "Invalid server name"
fi
