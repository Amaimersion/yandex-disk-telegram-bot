#!/bin/bash

TEMP_FILE="./scripts/telegram/temp.json"

touch $TEMP_FILE

echo "{" >> $TEMP_FILE
echo '"offset": "'$2'",' >> $TEMP_FILE
echo '"limit": 3,' >> $TEMP_FILE
echo '"timeout": 0,' >> $TEMP_FILE
echo "}" >> $TEMP_FILE

source ./scripts/telegram/telegram.sh \
  "getUpdates" \
  $1 \
  "--header Content-Type:application/json" \
  "--request POST" \
  "--data @$TEMP_FILE" \
  ${@:3}

rm $TEMP_FILE
