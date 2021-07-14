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
  - [Environment variables](#environment-variables)
  - [Server](#server)
    - [What the app uses](#what-the-app-uses)
    - [What you should use](#what-you-should-use)
  - [Database](#database)
    - [What the app uses](#what-the-app-uses-1)
    - [What you should use](#what-you-should-use-1)
  - [Background tasks](#background-tasks)
    - [What the app uses](#what-the-app-uses-2)
    - [How to use that](#how-to-use-that)
  - [Expose local server](#expose-local-server)
    - [What the app uses](#what-the-app-uses-3)
    - [What you should use](#what-you-should-use-2)
  - [Translations](#translations)
    - [What the app uses](#what-the-app-uses-4)
    - [How to use that](#how-to-use-that-1)
- [Deployment](#deployment)
  - [Before](#before)
  - [Heroku](#heroku)
    - [First time](#first-time)
    - [What's next](#whats-next)
  - [VPS](#vps)
- [Docker](#docker)
  - [Deployment](#deployment-1)
  - [Development](#development)
  - [Data](#data)
  - [Backups](#backups)
  - [Resources](#resources)
- [Version naming](#version-naming)
- [Contribution](#contribution)
  - [Translations](#translations-1)
- [License](#license)


## Features

- uploading of photos (limit is 20 MB),
- uploading of files (limit is 20 MB),
- uploading of audio (limit is 20 MB),
- uploading of video (limit is 20 MB),
- uploading of voice (limit is 20 MB),
- uploading of files using direct URL,
- uploading of various resources (YouTube, for example) with help of `youtube-dl`,
- uploading for public access,
- publishing and unpublishing of files or folders,
- creating of folders,
- getting information about a file, folder or disk.


## Requirements

- [python 3.8+](https://www.python.org/)
- [pip](https://pypi.org/project/pip/)
- [venv](https://docs.python.org/3/library/venv.html)
- [git](https://git-scm.com/)
- [curl](https://curl.haxx.se/) (optional)
- [nginx 1.16+](https://nginx.org/) (optional)
- [postgreSQL 10+](https://www.postgresql.org/) (optional)
- [redis 6.0+](https://redis.io/) (optional)
- [heroku 7.39+](https://www.heroku.com/) (optional)
- [ngrok 2.3+](https://ngrok.com/) (optional)
- [docker 20.10+](https://www.docker.com/) (optional)
- [docker-compose 1.29+](https://www.docker.com/) (optional)

It is expected that all of the above software is available as a global variables: `python3`, `python3 -m pip`, `python3 -m venv`, `git`, `curl`, `nginx`, `psql`, `heroku`, `ngrok`, `docker`, `docker-compose`. See [this](https://github.com/pypa/pip/issues/5599#issuecomment-597042338) why you should use such syntax: `python3 -m <module>`.

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
```

And activate it:

```shell
source ./venv/bin/activate
```

Run `deactivate` when you end in order to exit from virtual environment or just close terminal window.

After that step we will use `python` instead of `python3` and `pip` instead of `python3 -m pip`. If for some reason you don't want create virtual environment, then:
- use `python3` and `python3 -m pip`,
- edit executable paths in `.vscode/settings.json`,
- edit names in `./scripts` files.

You probably need to upgrade `pip`, because [you may have](https://github.com/pypa/pip/issues/5221) an old version (9.0.1) instead of new one. Run `pip install --upgrade pip`.

3. Install requirements.

```shell
./scripts/requirements/install.sh
```

4. Set environment variables.

```shell
source ./scripts/env/<name>.sh
```

Where `<name>` is either `production`, `development` or `testing`. Start with `development` if you don't know what to use.

These environment variables are required to create right app configuration, which is unique for specific environemts. For example, you can have different `DATABASE_URL` variable for `production` and `development`.

You need these environment variables every time when you implicitly interact with app configuration. For example, DB upgrade and background workers implicitly create app and use it configuration.

If you forgot to set environment variables but they are required to configure the app, you will get following error: `Unable to map configuration name and .env.* files`.

5. If you want to use database locally, then make DB upgrade:

```shell
flask db upgrade
```

6. Run this to see more available actions:

```shell
python manage.py --help
```

7. Every time when you open this project again, don't forget to activate virtual environment.

That's all you need to set up this project. If you want to set up fully working app, then:

1. Perform [integration with external API's](#integration-with-external-apis).

2. See [Local usage](#local-usage) for `development` and [Deployment](#deployment) for `production`.


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

For parameter `MAX_CONNECTIONS` it is recommended to use maxium number of simultaneous connections to the selected database. For example, "Heroku Postgres" extension at "Hobby Dev" plan have connection limit of 20. So, you should use `20` as a value for `MAX_CONNECTIONS` parameter in order to avoid possible `Too many connections` error.

From Telegram documentation:
> If you'd like to make sure that the Webhook request comes from Telegram, we recommend using a secret path in the URL, e.g. `https://www.example.com/<token>`. Since nobody else knows your bot‘s token, you can be pretty sure it’s us.

So, instead of `/telegram_bot/webhook` you can use something like this: `/telegram_bot/webhook_fd1k3Bfa01WQl5S`. To achieve this set environment variable `TELEGRAM_API_WEBHOOK_URL_POSTFIX`. In that case it is `TELEGRAM_API_WEBHOOK_URL_POSTFIX=_fd1k3Bfa01WQl5S`.

### Yandex.Disk

1. Register your app in [Yandex](https://yandex.ru/dev/oauth/). Sometimes it can take a while for Yandex moderators to check your app.

2. Get your app ID and password at special Yandex page for your app.

3. At special Yandex page for your app find "Callback URI" setting and add this URI: `https://<your site>/telegram_bot/yandex_disk_authorization`. It is required if you want to use `AUTO_CODE_CLIENT` Yandex.OAuth method, which is configured by default.


## Local usage

### Environment variables

In a root directory create `.env.development` file and fill it based on `.env.example` file.

### Server

#### What the app uses

This WSGI App uses `gunicorn` as WSGI HTTP Server and `nginx` as HTTP Reverse Proxy Server. For development purposes only `flask` built-in WSGI HTTP Server is used.

`flask` uses `http://localhost:8000`, `gunicorn` uses `unix:/tmp/nginx-gunicorn.socket` or `http://0.0.0.0:8080`, `nginx` uses `http://localhost:80`. Make sure these addresses is free for usage, or change specific server configuration.

`nginx` will not start until `gunicorn` creates `/tmp/gunicorn-ready` file. Make sure you have access rights to create this file.

By default `gunicorn` listens on unix socket instead of ip socket. You can enable ip socket by setting `GUNICORN_USE_IP_SOCKET` environment variable.

Open terminal and move in project root. Run `./scripts/wsgi/<environment>.sh <server>` where `<environment>` is either `prodction`, `development` or `testing`, and `<server>` is either `flask`, `gunicorn` or `nginx`. Example: `./scripts/wsgi/production.sh gunicorn`.

Usually you will want to run both `gunicorn` and `nginx`. To do so run scripts in separate terminals (recommend way). After that visit `nginx` address.

Run `./scripts/server/stop_nginx.sh` in order to stop nginx.

nginx uses simple configuration from `./src/configs/nginx.conf`. You can ignore this and use any configuration for nginx that is appropriate to you. However, it is recommended to use exact configurations as in app for both `flask` and `gunicorn`. If you think these configurations is not good, then make PR instead.

#### What you should use

For active development it will be better to use only `flask` WSGI HTTP Server.

```shell
source ./scripts/wsgi/development.sh flask
```

That command will automatically set environment variables and run `flask` WSGI server. And your app will be fully ready for incoming requests.

If you want to test more stable and reliable configuration which will be used in production, then run these commands in separate terminal window.

```shell
source ./scripts/wsgi/development.sh gunicorn
```

```shell
source ./scripts/server/stop_nginx.sh
source ./scripts/wsgi/development.sh nginx
```

### Database

#### What the app uses

In both development and testing environments `SQLite` is used. For production `PostgreSQL` is recommended, but you can use any of [supported databases](https://docs.sqlalchemy.org/en/13/core/engines.html#supported-databases). App already configured for both `SQLite` and `PostgreSQL`, for another database you may have to install additional Python packages.

By default both development and testing databases will be located at `src/temp.sqlite`. If you want to use different name for DB, then specify value for `DATABASE_URL` in `.env.development` and `.env.testing` files.

`Redis` database is supported and expected, but not required. However, it is highly recommended to enable it, because many useful features of the app depends on `Redis` functionality and they will be disabled in case if `Redis` is not configured using `REDIS_URL`.

#### What you should use

Usually it will be better to manually specify DB name in `.env.development` and specify `REDIS_URL`. Try to always use `Redis`, including development environment. If you decide not to enable `Redis`, it is fine and you still can use the app with basic functionality which don't depends on `Redis`.

### Background tasks

#### What the app uses

`RQ` is used as a task queue. `Redis` is required.

Examples of jobs that will be enqueued: monitoring of uploading status and uploading of files.

The app is not ready to support other task queues. You may need to make changes on your own if you decide to use another task queue.

#### How to use that

It is highly recommended that you run at least one worker.

1. Make sure `REDIS_URL` is specified.
2. Open separate terminal window.
3. Activate `venv` and set environment variables.
4. Run: `python manage.py run-worker`

These steps will run one worker instance. Count of workers depends on your expected server load. For `development` environment recommend count is 2.

Note that `RQ` will not automatically reload your running workers when source code of any job function's changes. So, you should restart workers manually.

### Expose local server

#### What the app uses

`ngrok` is used to expose local server. It is free and suitable for development server.

#### What you should use

You can use whatever you want. But if you decide to use `ngrok`, the app provides fews utils to make it easier.

Before:
- requests will be routed to `/telegram_bot/webhook`, so, make sure you didn't change this route,
- you also should have [jq](https://stedolan.github.io/jq/) on your system.

Then:

1. Run `flask` server:

```shell
source ./scripts/wsgi/development.sh flask
```

2. In separate terminal window run `ngrok`:

```shell
source ./scripts/ngrok/run.sh
```

3. In separate terminal window set a webhook:

```shell
source ./scripts/ngrok/set_webhook.sh <TELEGRAM_API_BOT_TOKEN>
```

Where `<TELEGRAM_API_BOT_TOKEN>` is your Telegram bot API token for specific environment (you can have different bots for different environments).

### Translations

#### What the app uses

Translations are built on top of `Babel`, which provides support for GNU `gettext`.

#### How to use that

If you want to enable translations, then before server start you should compile existing raw translations:

```shell
python manage.py compile-translations
```

If you want to update existing translations to match actual app state, then run this, edit changed lines in translations files, and recompile updated translations:

```shell
python manage.py update-translations
```

If you want to add translations for new language, then run this, fill translations file, and recompile updated translations:

```shell
python manage.py init-translations <SMALL LETTERS LANGUAGE CODE>
```


## Deployment

Regardless of any platform you choose for hosting, it is recommended to manually configure number of workers, number of workers connections and number of threads for both `gunicorn` and `nginx`.

### Before

It is recommended to run linters with `source ./scripts/linters/all.sh` before deployment and resolve all errors and warnings.

### Heroku

It is a way to host this app for free. And that will be more than enough until you have hundreds of active users.

#### First time

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

5. We need Heroku `Redis` addon in order to use that database.

```
heroku addons:create heroku-redis:hobby-dev
```

6. Set required environment variables:

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

7. Switch to a new branch that is special for Heroku (don't ever push it!):

```git
git checkout -b heroku
```

If that branch already created, then just type:

```
git checkout heroku
```

8. Make sure `.env.production` file is created and filled. Remove it from `.gitignore`. Don't forget: don't ever push it anywhere but Heroku.

9. Add changes for pushing to Heroku:

- if you edited files on `heroku` branch:
```git
git add
git commit -m <message>
```

- if you want push changes from another branch:
```git
git merge <another branch> -m <message>
```

10. Upload files to Heroku:

```git
git push heroku heroku:master
```

11. Set number of workers for background tasks. On free plan you cannot use more than 1 worker.

```
heroku scale worker=1
```

#### What's next

You should do steps № 7, 9 and 10 every time when you want to push changes.

### VPS

Use [docker](#docker) or see [installation](#installation).


## Docker

This project provides Docker images along with configured docker-compose file. Usage of docker-compose is recommended way to deploy or run this application.

### Deployment

1. Clone this repository.

2. In the root directory create `.env.production` file and fill it based on `.env.example` file.

3. Run docker-compose:

```shell
docker-compose up
```

You don't need to configure any process control system in order to run docker-compose in background on every system start. It is already done by Docker daemon.

4. By default docker-compose will listen for connections on `http://127.0.0.1:8080`. It is recommended to set up some reverse proxy server (along with TLS, logs and so on) in the front of docker-compose and redirect connections on that address. Or you can override docker-compose configuration to listen for connections immediately on `http://127.0.0.1:80`.

### Development

You can run docker-compose in development workflow.

1. Clone this repository.

2. In the root directory create `.env.development` file and fill it based on `.env.example` file.

3. Run docker-compose:

```shell
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Keep in mind that [data](#data) that already stored in `./var` folder will be used. If there is no data, then new one will be created. It is means that [data](#data) is common for both development and production. If you don't want this behavior, then consider to create several clones of the project or override docker-compose config.

4. Run ngrok to handle incoming connections:

```shell
source ./scripts/ngrok/run.sh 8080
```

5. Set a webhook:

```shell
source ./scripts/ngrok/set_webhook.sh <TELEGRAM_API_BOT_TOKEN>
```

6. After that you can edit code in `./src` folder. Hot reloading is enabled.

### Data

By default docker-compose will store data of some services locally on a host machine. It is persistent data that stores state of your app, so, don't delete it.

`PostgreSQL` will store its data in `./var/lib/postgresql/data` folder. `Redis` will store its data in `./var/lib/redis`.

Most probably you shouldn't interact with that data directly. Instead, consider to make [backups](#backup).

### Backups

On some point you may want to backup your `PostgreSQL` data. Don't copy/paste `./var/lib/postgresql/data` folder. Instead, perform following commands:

- to backup data, run on a host machine:

```shell
docker exec -t yd-tg-bot-postgres pg_dump -U <POSTGRES_USER> -d <POSTGRES_DB> > dump.sql
```

- to restore data, run on a host machine:

```shell
cat dump.sql | docker exec -i yd-tg-bot-postgres psql -U <POSTGRES_USER> -d <POSTGRES_DB>
```

`dump.sql` is entire backup of your DB. Keep it somewhere safe, outside of host machine.

Feel free to modify above commands. It is just an example of how to do it. You can even use your own way to backup/restore your data.

Before restoring `<POSTGRES_DB>` database should be clean, but created. By default the app upgrades database at startup, which means that database will have some data. You will need to manually drop and create database:

```shell
docker exec -it yd-tg-bot-postgres psql -U <POSTGRES_USER> -d postgres
DROP DATABASE <POSTGRES_DB>;
CREATE DATABASE <POSTGRES_DB>;
```

Keep in mind that database have encrypted data in some tables. It is means that you should use exact a same `FLASK_SECRET_KEY` environment variable that was used at the moment of database backup. You will be not able to fully interact with database if you will use different `FLASK_SECRET_KEY`. So, usually you will also want to backup your `.env.production` file in order to keep your secrets.

### Resources

This project have `gunicorn` and `rq`, which have workers that creating fork of parent process. It is means extensive usage of machine resources, particularly RAM.

Consider your host machine resources when you configuring `GUNICORN_WORKERS`, `RQ_WORKERS` and other settings that may affect as usage of machine resources. Use these commands to monitor usage of resources:

```shell
docker stats
```

```shell
docker-compose top
```


## Version naming

This project uses following structure for version naming: `<MAJOR CHANGES>.<BIG CHANGES>.<SMALL CHANGES>`.

- "Major changes" usually means really cardinal changes. Such changes may require from developers to set up application again, inspect new technical stack and app architecture. It is certainly incompatible with the earlier application code.
- "Big changes" usually means new features, big changes or long-awaited bug fixes. Such changes may require big time to test and complete. Main development workflow goes here.
- "Small changes" usually means some small changes or fast bug fixes. Most likely every version will contain small amount of changes.


## Contribution

Feel free to use [issues](https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/new). [Pull requests](https://github.com/Amaimersion/yandex-disk-telegram-bot/compare) are also always welcome!

### Translations

If you want to translate this app, then you will need to perform following steps:

1. Make sure you [installed](#installation) the project.

2. Run:

```shell
python manage.py init-translations <LANGUAGE CODE>
```

3. Fill new translation file that is located at `translations/<LANGUAGE CODE>/LC_MESSAGES/messages.po`.

Next step is not mandatory for you and can be performed by project owner. You can just create a PR with result from step up to № 3. However, next changes are required in order to enable new translation.

4. Make code changes according to these commits: [d6bc3fe](https://github.com/Amaimersion/yandex-disk-telegram-bot/commit/d6bc3fe3ff8ebdab9d390b88c7f26bd5f609f434), [9a34008](https://github.com/Amaimersion/yandex-disk-telegram-bot/commit/9a34008f4dae537790a210e4fc30388fbb3c25b6). Actual code may be slightly different.


## License

[MIT](https://github.com/Amaimersion/yandex-disk-telegram-bot/blob/master/LICENSE).
