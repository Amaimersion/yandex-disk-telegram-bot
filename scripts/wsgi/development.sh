#!/bin/bash

export FLASK_ENV=development
export CONFIG_NAME=development

source ./scripts/wsgi/server.sh
