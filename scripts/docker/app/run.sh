#!/bin/bash

flask db upgrade
source ./scripts/server/run.sh gunicorn
