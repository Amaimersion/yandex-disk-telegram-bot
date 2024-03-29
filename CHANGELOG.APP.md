This changelog includes records about notable changes that are only visible from developer side. Such records require some technical expertise to properly understand them. To see changelog from end user side, see [changelog for end users](CHANGELOG.md).
___


# 1.3.1 (August 27, 2021)

## Fixed

- Invalid template for production logger.


# 1.3.0 (August 27, 2021)

## Added

- Support for `callback_query` Telegram update.
- Support for user settings.
- Support for translations.
- `gunicorn` will support IP socket configuration through `GUNICORN_USE_IP_SOCKET` and `GUNICORN_PORT` env variables.
- path of unix socket for `gunicorn` server can be changed through `GUNICORN_UNIX_SOCKET_PATH` env variable.
- Docker images.
- Support for docker-compose.
- Information about project version naming.
- Short name in information about the app.
- Logger settings for `Flask` and `gunicorn`. Set it through env variables.
- Debug logs.

## Changed

- Big refactoring.
- Changelog splitted into two files: one for end users and one for developers.
- Changelog will no longer contain `Improved` section. It will be merged with `Changed` section.
- DB data about incoming Telegram user will be fetched on every request, before dispatching of request to appropriate handler.
- `language` column moved from `User` model to `UserSettings`.
- Background tasks will have copy of request `g` data.
- Worker for background tasks should be started with `python manage.py run-worker` instead of `python worker.py`.
- To add webhook URL postfix use `TELEGRAM_API_WEBHOOK_URL_POSTFIX` env variable, from now don't edit `views.py` file and revert it back.
- SQLAlchemy debug echo will be disabled by default. Use `SQLALCHEMY_ECHO` env variable to control it.
- Python runtime version to 3.8.11.
- `src.api` module renamed to `src.http`.

## Fixed

- `/telegram_bot/yandex_disk_authorization` with trailing slash at the end (i.e., `/telegram_bot/yandex_disk_authorization/`) will be handled correctly.
- Invalid DB migrations for PostgreSQL. More specifically, these migrations didn't really change enum values. That bug was not noticeable, because new enum values wasn't actually used at all. For SQLite everything was ok. To fix invalid PostgreSQL schema, run `flask db downgrade 358b1cefda13 && flask db upgrade`. You will not lose your current data (at the moment of `20dfdf679e84` migration).


# 1.2.0 (December 14, 2020)

## Improved

- Upgrade `python` to 3.8.5.
- All requirements upgraded to latest version.
- Big refactoring.

## Added

- Stateful chat support. Now bot can store custom user data (in different namespaces: user, chat, user in chat); determine Telegram message types; register single use handler (call once for message) with optional timeout for types of message; subscribe handlers with optional timeout for types of messages.
- [Console Client](https://yandex.ru/dev/oauth/doc/dg/reference/console-client.html) Yandex.OAuth method. By default it is disabled, and default one is [Auto Code Client](https://yandex.ru/dev/oauth/doc/dg/reference/auto-code-client.html/).
- RQ (job queue). It requires Redis to be enabled, and as Redis it is also optional. However, it is highly recommended to use it.
- Support for different env-type files (based on current environment). Initially it was only for production.
- Web Site: 302 (redirect to Telegram) will be returned instead of 404 (not found page), but only in production mode.
- Debug configuration for VSCode.
- DB: add indexes for frequent using columns.

## Changed

- Redirect to favicon will be handled by nginx.
- Biggest photo (from single photo file) will be selected based on total pixels count, not based on height.

## Fixed

- A bug when new user (didn't use any command before) used `/revoke_access` command and it led to request crash (500).
- Situation: Telegram send an update, the server sent back a 500; Telegram will send same update again and again until it get 200 from a server, but server always returns 500. Such sitations can occur, for example, when user initiated a command and blocked the bot - bot can't send message to user in this case (it gets 403 from Telegram API, so, server raises error because it is an unexpected error and should be logged). Now it is fixed and the bot always send back 200, even for such error situations.


# 1.1.0 (May 9, 2020)

## Improved

- Big refactoring of everything.
- File structure.
- Upgrade `gevent` to 1.5.0.

## Added

- `SERVER_NAME` environment variable.
- Google Analytics in authorization pages.
- Templates for issues and pull requests.
- `robots.txt`.

## Changed

- Decreased size of slug on Heroku by removing unused files and folders.
- Decreased number of seconds for Yandex.OAuth request timeout.
- Redirects and generated URL's always will be absolute URL's with `PREFERRED_URL_SCHEME + SERVER_NAME`.
- If user refused to grant the access to Yandex.Disk, then user `insert_token` will be cleared after redirect.


# 1.0.0 (April 15, 2020)

Initial release!
