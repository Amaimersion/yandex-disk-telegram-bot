#!/bin/bash

export FLASK_ENV=production
export CONFIG_NAME=production

source ./scripts/wsgi/server.sh
