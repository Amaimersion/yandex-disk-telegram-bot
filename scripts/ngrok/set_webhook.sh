#!/bin/bash

ngrok_url=`curl http://localhost:4040/api/tunnels/command_line --silent --show-error | jq '.public_url' --raw-output`
webhook_url="$ngrok_url/telegram_bot/webhook"
bot_token=$1
max_connections=30

source ./scripts/telegram/set_webhook.sh $bot_token $webhook_url $max_connections
