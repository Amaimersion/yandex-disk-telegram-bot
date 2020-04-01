#!/bin/bash

TEMP_FILE="./scripts/telegram/temp.json"

touch $TEMP_FILE

echo "{" >> $TEMP_FILE
echo '"chat_id": '$2',' >> $TEMP_FILE
echo '"text": "'$3'",' >> $TEMP_FILE
echo "}" >> $TEMP_FILE

source ./scripts/telegram/telegram.sh \
  "sendMessage" \
  $1 \
  "--header Content-Type:application/json" \
  "--request POST" \
  "--data @$TEMP_FILE" \
  ${@:4}

rm $TEMP_FILE
