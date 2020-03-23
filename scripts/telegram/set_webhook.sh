#!/bin/bash

TEMP_FILE="./scripts/telegram/temp.json"

touch $TEMP_FILE

echo "{" >> $TEMP_FILE
echo '"url": "'$2'",' >> $TEMP_FILE
echo '"max_connections": 50,' >> $TEMP_FILE
echo '"allowed_updates": ["message", "edited_message"]' >> $TEMP_FILE
echo "}" >> $TEMP_FILE

source ./scripts/telegram/telegram.sh \
  "setWebhook" \
  $1 \
  "--header Content-Type:application/json" \
  "--request POST" \
  "--data @$TEMP_FILE" \
  ${@:3}

rm $TEMP_FILE
