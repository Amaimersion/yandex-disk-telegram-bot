#!/bin/bash

export FLASK_ENV=development
export CONFIG_NAME=testing

source ./scripts/wsgi/server.sh
