#!/bin/bash

export FLASK_ENV=production
export CONFIG_NAME=production

source ./scripts/server/run.sh
