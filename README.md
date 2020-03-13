<h1 align="center">
  Yandex.Disk in Telegram
</h1>

<p align="center">
  A bot for Telegram that integrates Yandex.Disk right into Telegram.
</p>

## Content

- [Content](#content)
- [Requirements](#requirements)
- [Installation](#installation)
- [Deployment](#deployment)

## Requirements

- [Python 3.6+](https://www.python.org/)
- [Pip](https://pypi.org/project/pip/)
- [Venv](https://docs.python.org/3/library/venv.html)
- [Git](https://git-scm.com/)
- [Curl](https://curl.haxx.se/)

It is expected that all of the above software is available as a global variable: `python3`, [`python3 -m pip`](https://github.com/pypa/pip/issues/5599#issuecomment-597042338), `python3 -m venv`, `git`, `curl`.

If you want to host this server somewhere, then you need install additional software. See your host installation guide.

All subsequent instructions is for Unix systems (primarily for Linux). You may need to make some changes on your own if you work on Windows.

## Installation

1. Clone this repository.

```shell
git clone https://github.com/Amaimersion/yandex-disk-telegram-bot.git
cd yandex-disk-telegram-bot
```

2. Create virtual environment.

```shell
python3 -m venv venv
source ./venv/bin/activate
```

Run `deactivate` when you end in order to exit from virtual environment.

After that step we will use `python` instead of `python3` and `pip` instead of `python3 -m pip`. If for some reason you don't want create virtual environment, then:
- use `python3` and `python3 -m pip`
- edit executable paths in `.vscode/settings.json`
- edit names in `./scripts` files

You may also want to upgrade `pip`, because [there can be](https://github.com/pypa/pip/issues/5221) an old version (9.0.1) instead of new one. Run `pip install --upgrade pip`.

3. Install requirements.

```shell
./scripts/requirements/install.sh
```

## Deployment

token - https://yandex.ru/dev/disk/rest/
token - telegram
