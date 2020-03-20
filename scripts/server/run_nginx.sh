#!/bin/bash

SERVER_READY_FILE="/tmp/gunicorn-ready"

# we will wait until the WSGI HTTP Server starts up.
# so, when nginx starting, the app is ready for traffic.
while [[ ! -f "$SERVER_READY_FILE" ]]; do
  echo "Waiting for WSGI HTTP Server start"
  sleep 1
done

sudo nginx -p $PWD -c $PWD/src/configs/nginx.conf
