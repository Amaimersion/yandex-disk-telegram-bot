<h1 align="center">
  Yandex.Disk in Telegram
</h1>

<p align="center">
  A bot for Telegram that integrates Yandex.Disk right into Telegram.
</p>

## Content

- [Content](#content)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Integration with external API's](#integration-with-external-apis)
  - [Telegram](#telegram)
  - [Yandex.Disk](#yandexdisk)
- [Local usage](#local-usage)
- [Deployment](#deployment)
  - [Heroku](#heroku)
- [Contribution](#contribution)
- [License](#license)

## Features

Nothing here yet.

## Requirements

- [python 3.8+](https://www.python.org/)
- [pip](https://pypi.org/project/pip/)
- [venv](https://docs.python.org/3/library/venv.html)
- [git](https://git-scm.com/)
- [curl](https://curl.haxx.se/) (optional)
- [nginx](https://nginx.org/) (optional)

It is expected that all of the above software is available as a global variable: `python3`, [`python3 -m pip`](https://github.com/pypa/pip/issues/5599#issuecomment-597042338), `python3 -m venv`, `git`, `curl`, `nginx`.

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

## Integration with external API's

### Telegram

telegram

### Yandex.Disk

https://yandex.ru/dev/disk/rest/

## Local usage

This WSGI App uses `gunicorn` as WSGI HTTP Server and `nginx` as HTTP Reverse Proxy Server. For development purposes `flask` built-in WSGI HTTP Server is used.

`gunicorn` and `flask` uses `http://localhost:8000`, `nginx` uses `http://localhost:80`. Make sure these addresses is free for usage, or change specific server configuration.

Open terminal and move in project root. Run `./scripts/wsgi/<environment>.sh <server>` where `<environment>` is either `prodction`, `development` or `testing`, and `<server>` is either `flask`, `gunicorn` or `nginx`. Example: `./scripts/wsgi/production.sh gunicorn`.

In order to run both `gunicorn` and `nginx` run scripts in separate terminals (recommend way). After that visit `http://localhost:80` which will redirect to `http://localhost:8000`.

Run `./scripts/server/stop_nginx.sh` in order to stop nginx.

nginx uses simple configuration from `./src/configs/nginx.conf`. You can ignore this and use any configuration for nginx that is appropriate to you. However, it is recommend to use exact configuration as in current version for `flask` and `gunicorn`. Instead, make PR if you think that something is wrong with these two configurations.

## Deployment

### Heroku

1. If you don't have [Heroku](https://heroku.com/) installed, then it is a time to do that.

2. If you don't have Heroku remote, then add it:
- for existing app:
```git
git remote add heroku <URL>
```
- for new app:
```
heroku create
```

3. Switch to new branch (don't ever push it!):
```git
git checkout -b heroku
```

4. Make sure `.env` file is created. Remove it from `.gitignore`. Don't forget: don't ever push it anywhere but Heroku.

5. Add changes for pushing to Heroku:
```git
git add .
git commit -m "heroku"
```

6. Upload files to Heroku:
```git
git push heroku heroku:master
```

## Contribution

Feel free to use [issues](https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/new). [Pull requests](https://github.com/Amaimersion/yandex-disk-telegram-bot/compare) are also always welcome!


## License

[MIT](https://github.com/Amaimersion/yandex-disk-telegram-bot/blob/master/LICENSE).
