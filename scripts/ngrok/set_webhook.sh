#!/bin/bash

ngrok_url=`curl http://localhost:4040/api/tunnels/command_line --silent --show-error | jq '.public_url' --raw-output`
webhook_url="$ngrok_url/telegram_bot/webhook"
bot_token=$1
max_connections=30

if [ -z $bot_token ]; then
  echo "Bot token not specified manually. Will try to read it from .env.development file"

  if [ -e .env.development ]; then
    bot_token=$(cat .env.development | grep -o -P '(?<=TELEGRAM_API_BOT_TOKEN=)(\d+)(.*)')
  fi
fi

if [ -z $bot_token ]; then
  echo "Bot token is missing"
  return 1
fi

source ./scripts/telegram/set_webhook.sh $bot_token $webhook_url $max_connections
