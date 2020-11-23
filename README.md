<h1 align="center">
  Yandex.Disk in Telegram
</h1>

<p align="center">
  A Telegram bot that integrates Yandex.Disk into Telegram.
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
  - [Server](#server)
  - [Database](#database)
- [Deployment](#deployment)
  - [Before](#before)
  - [Heroku](#heroku)
- [Contribution](#contribution)
- [License](#license)


## Features

- uploading of photos (limit is 20 MB).
- uploading of files (limit is 20 MB).
- uploading of files using direct URL.
- uploading of audio (limit is 20 MB).
- uploading of video (limit is 20 MB).
- uploading of voice (limit is 20 MB).
- uploading for public access.
- publishing and unpublishing of files or folders.
- creating of folders.
- getting of information about file, folder or disk.


## Requirements

- [python 3.8+](https://www.python.org/)
- [pip](https://pypi.org/project/pip/)
- [venv](https://docs.python.org/3/library/venv.html)
- [git](https://git-scm.com/)
- [curl](https://curl.haxx.se/) (optional)
- [nginx 1.16+](https://nginx.org/) (optional)
- [postgreSQL 10+](https://www.postgresql.org/) (optional)
- [heroku 7.39+](https://www.heroku.com/) (optional)

It is expected that all of the above software is available as a global variable: `python3`, `python3 -m pip`, `python3 -m venv`, `git`, `curl`, `nginx`, `psql`, `heroku`. See [this](https://github.com/pypa/pip/issues/5599#issuecomment-597042338) why you should use such syntax: `python3 -m <module>`.

All subsequent instructions is for Unix-like systems, primarily for Linux. You may need to make some changes on your own if you work on non-Linux operating system.

If you want to host this server somewhere outside of Heroku, then you may need to install additional software. See your host installation guide.


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

You probably need to upgrade `pip`, because [you may have](https://github.com/pypa/pip/issues/5221) an old version (9.0.1) instead of new one. Run `pip install --upgrade pip`.

3. Install requirements.

```shell
./scripts/requirements/install.sh
```

4. If you want to use database locally, then make DB upgrade:

```shel
source ./scripts/env/development.sh
flask db upgrade
```

5. Run this to see more actions:

`python manage.py --help`

That's all you need for development. If you want create production-ready server, then:

1. Perform [integration with external API's](#integration-with-external-apis).

2. See [Local usage](#local-usage) or [Deployment](#deployment).


## Integration with external API's

### Telegram

1. Register your bot in chat with [@BotFather](http://t.me/BotFather) and get API token.

2. [Set a webhook](https://core.telegram.org/bots/api#setwebhook):

```shell
./scripts/telegram/set_webhook.sh <TELEGRAM_BOT_TOKEN> <SERVER_URL> <MAX_CONNECTIONS>
```

Russian users may need a proxy:
```shell
./scripts/telegram/set_webhook.sh <TELEGRAM_BOT_TOKEN> <SERVER_URL> <MAX_CONNECTIONS> "--proxy <PROXY>"
```

For parameter `MAX_CONNECTIONS` it is recommended to use maxium number of simultaneous connections to the selected database. For example, "Heroku Postgres" extension at "Hobby Dev" plan have connection limit of 20. So, you should use `20` as value for `MAX_CONNECTIONS` parameter in order to avoid possible `Too many connections` error.

From Telegram documentation:
> If you'd like to make sure that the Webhook request comes from Telegram, we recommend using a secret path in the URL, e.g. `https://www.example.com/<token>`. Since nobody else knows your bot‘s token, you can be pretty sure it’s us.

So, instead of `/telegram_bot/webhook` you can use something like this: `/telegram_bot/webhook_fd1k3Bfa01WQl5S`.

### Yandex.Disk

1. Register your app in [Yandex](https://yandex.ru/dev/oauth/). Most likely it will take a while for Yandex moderators to check your app.

2. Get your app ID and password at special Yandex page for your app.

3. At special Yandex page for your app find "Callback URI" setting and add this URI: `https://<your site>/telegram_bot/yandex_disk_authorization`.


## Local usage

### Server

This WSGI App uses `gunicorn` as WSGI HTTP Server and `nginx` as HTTP Reverse Proxy Server. For development purposes `flask` built-in WSGI HTTP Server is used.

`flask` uses `http://localhost:8000`, `gunicorn` uses `unix:/tmp/nginx-gunicorn.socket`, `nginx` uses `http://localhost:80`. Make sure these addresses is free for usage, or change specific server configuration.

`nginx` will not start until `gunicorn` creates `/tmp/gunicorn-ready` file. Make sure you have access to create this file.

Open terminal and move in project root. Run `./scripts/wsgi/<environment>.sh <server>` where `<environment>` is either `prodction`, `development` or `testing`, and `<server>` is either `flask`, `gunicorn` or `nginx`. Example: `./scripts/wsgi/production.sh gunicorn`.

Usually you will want to run both `gunicorn` and `nginx`. To do so run scripts in separate terminals (recommend way). After that visit `nginx` address.

Run `./scripts/server/stop_nginx.sh` in order to stop nginx.

nginx uses simple configuration from `./src/configs/nginx.conf`. You can ignore this and use any configuration for nginx that is appropriate to you. However, it is recommended to use exact configurations as in app for both `flask` and `gunicorn`. If you think these configurations is not right, then make PR instead.

### Database

In both development and testing environments `SQLite` is used. For production `PostgreSQL` is recommended, but you can use any of [supported databases](https://docs.sqlalchemy.org/en/13/core/engines.html#supported-databases). App already configured for both `SQLite` and `PostgreSQL`, for another database you may have to install additional Python packages.

Development and testing databases will be located at `src/development.sqlite` and `src/testing.sqlite` respectively.


## Deployment

Regardless of any platform you choose for hosting, it is recommended to manually configure number of workers, number of workers connections and number of threads for both `gunicorn` and `nginx`.

### Before

It is recommended to run linters with `./scripts/linters/all.sh` before deployment and resolve all errors and warnings.

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

3. We need both python and nginx build packs. Python build pack should be added automatically, but we will do it manually. For nginx build pack you can use whatever you want: [official one](https://github.com/heroku/heroku-buildpack-nginx), [my own one](https://github.com/Amaimersion/heroku-buildpack-nginx-for-yandex-disk-telegram-bot) or create your own one. In case of not using my own nginx build pack don't forget about compatibility (config paths, environment variables names, etc.).

```
heroku buildpacks:set heroku/python
heroku buildpacks:add https://github.com/Amaimersion/heroku-buildpack-nginx-for-yandex-disk-telegram-bot.git
```

4. We need Heroku `PostgreSQL` addon in order to use that database.

```
heroku addons:create heroku-postgresql:hobby-dev
```

Later you can view the DB content by using `heroku pg:psql`.

5. Set required environment variables:

```
heroku config:set SERVER_NAME=<your host without scheme>
```

You may also want to set recommended environment variables:

```
heroku config:set NGINX_WORKERS=<value>
heroku config:set NGINX_WORKER_CONNECTIONS=<value>
heroku config:set GUNICORN_WORKERS=<value>
heroku config:set GUNICORN_WORKER_CONNECTIONS=<value>
```

6. Switch to new branch special for Heroku (don't ever push it!):

```git
git checkout -b heroku
```

7. Make sure `.env.production` file is created and filled. Remove it from `.gitignore`. Don't forget: don't ever push it anywhere but Heroku.

8. Add changes for pushing to Heroku:

- if you edited files on heroku branch:
```git
git add .
git commit -m <message>
```

- if you want push changes from another branch:
```git
git merge <another branch> -m <message>
```

9. Upload files to Heroku:

```git
git push heroku heroku:master
```

You should do № 8 and № 9 every time you want to push changes.


## Contribution

Feel free to use [issues](https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/new). [Pull requests](https://github.com/Amaimersion/yandex-disk-telegram-bot/compare) are also always welcome!


## License

[MIT](https://github.com/Amaimersion/yandex-disk-telegram-bot/blob/master/LICENSE).
