#!/bin/bash

source ./scripts/telegram/telegram.sh \
  "deleteWebhook" \
  ${@}
