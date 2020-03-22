#!/bin/bash

response=$(
  curl \
  --silent \
  --show-error \
  ${@:3} \
  "https://api.telegram.org/bot$2/$1"
)

echo $response | python -m json.tool
