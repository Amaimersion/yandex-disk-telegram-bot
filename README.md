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

1. Create virtual environment.

```shell
python3 -m venv <path>
cd <path>
source ./bin/activate
```

Run `deactivate` when you end in order to exit from virtual environment.

After that step we will use `python` instead of `python3` and `pip` instead of `python3 -m pip`. If for some reason you don't want create virtual environment, then:
- use `python3` and `python3 -m pip`
- edit Python path in `.vscode/settings.json`

You may also want to upgrade `pip`, because [there can be](https://github.com/pypa/pip/issues/5221) an old version (9.0.1) instead of new one. Run `pip install --upgrade pip`.

2. Clone this repository.

```shell
git clone https://github.com/Amaimersion/yandex-disk-telegram-bot.git
cd <path>/yandex-disk-telegram-bot
```

3. Install dependencies.

```shell
pip install -r requirements.txt
```

## Deployment

token - https://yandex.ru/dev/disk/rest/
token - telegram
