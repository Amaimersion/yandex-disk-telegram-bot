#!/bin/bash

# we use `--exclude-editable` because after
# `pip install -e .` `pip freeze` gives
# `-e git+https://github.com/Amaimersion/yandex-disk-telegram-bot.git@d077e2481593e7a97e9f4014dc5dcdb92e85c1a9#egg=yandex_disk_telegram_bot`
# instead of `-e .`.
pip freeze > requirements.txt --exclude-editable
echo "-e ." >> requirements.txt
