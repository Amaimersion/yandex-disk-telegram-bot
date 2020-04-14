#!/bin/bash

gunicorn --config ./src/configs/gunicorn.py wsgi:app
