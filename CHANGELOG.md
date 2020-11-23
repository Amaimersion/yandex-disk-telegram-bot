# 1.2.0

## Telegram Bot

### Improved

- Text of some bot responses.

### Added

- `/public_upload_photo`, `/public_upload_file`, `/public_upload_audio`, `/public_upload_video`, `/public_upload_voice`, `/public_upload_url`: uploading of files and then publishing them.
- `/publish`: publishing of files or folders.
- `/unpublish`: unpublishing of files or folders.
- `/space`: getting of information about remaining Yandex.Disk space.
- `/element_info`: getting of information about file or folder.
- Handling of files that exceed file size limit in 20 MB. At the moment the bot will asnwer with warning message, not trying to upload that file. [#3](https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/3)
- Help messages for each upload command will be sended when there are no suitable input data.

### Changed

- `/create_folder`: now it will wait for folder name if you send empty command, not deny operation.
- `/upload`: on success it will return information about uploaded file, not plain status.
- `/upload_url`: result name will not contain parameters, queries and fragments.

### Fixed

- `/create_folder`: fixed a bug when bot could remove `/create_folder` occurrences from folder name.
- `/create_folder`: fixed a bug when bot don't send any responses on invalid folder name.
- Wrong information in help message for `/upload_video`.

## Project

### Improved

- Upgrade `python` to 3.8.5.
- All requirements upgraded to latest version.
- Big refactoring.

### Added

- Stateful chat support. Now bot can store custom user data (in different namespaces: user, chat, user in chat); determine Telegram message types; register single use handler (call once for message) with optional timeout for types of message; subscribe handlers with optional timeout for types of messages.
- [Console Client](https://yandex.ru/dev/oauth/doc/dg/reference/console-client.html) Yandex.OAuth method. By default it is disabled, and default one is [Auto Code Client](https://yandex.ru/dev/oauth/doc/dg/reference/auto-code-client.html/).
- Support for different env-type files (based on current environment). Initially it was only for production.
- Web Site: 302 (redirect to Telegram) will be returned instead of 404 (not found page), but only in production mode.
- Debug configuration for VSCode.

### Changed

- Redirect to favicon will be handled by nginx.
- Biggest photo (from single photo file) will be selected based on total pixels count, not based on height.

### Fixed

- A bug when new user (didn't use any command before) used `/revoke_access` command and it led to request crash (500).
- Situation: Telegram send an update, the server sent back a 500; Telegram will send same update again and again until it get 200 from a server, but server always returns 500. Such sitations can occur, for example, when user initiated a command and blocked the bot - bot can't send message to user in this case (it gets 403 from Telegram API, so, server raises error because it is an unexpected error and should be logged). Now it is fixed and the bot always send back 200, even for such error situations.


# 1.1.0 (May 9, 2020)

## Telegram Bot

### Improved

- Text of most bot responses.
- Text of authorization HTML pages.
- Style of authorization HTML pages.
- When uploading, bot will update single message instead of sending new one every time with operation status.

### Added

- `/upload_url`: uploading of file using direct URL.
- Privacy Policy and Terms & Conditions.
- Favicons for different platforms.
- Buttons with useful links in `/help` command.
- "Report a problem" link in error authorization HTML page.

### Changed

- Title.
- Description.
- Logo.
- Favicon.
- Button with URL instead of plain text with URL in `/grant_access` command.

### Fixed

- A bug when sometimes "I can't track operation status of this anymore. Perform manual checking." message could appear even if operation was completed.
- A bug when empty `/create_folder` was successfully handled.

## Project

### Improved

- Big refactoring of everything.
- File structure.
- Upgrade `gevent` to 1.5.0.

### Added

- `SERVER_NAME` environment variable.
- Google Analytics in authorization pages.
- Templates for issues and pull requests.
- `robots.txt`.

### Changed

- Decreased size of slug on Heroku by removing unused files and folders.
- Decreased number of seconds for Yandex.OAuth request timeout.
- Redirects and generated URL's always will be absolute URL's with `PREFERRED_URL_SCHEME + SERVER_NAME`.
- If user refused to grant the access to Yandex.Disk, then user `insert_token` will be cleared after redirect.


# 1.0.0 (April 15, 2020)

Initial release!
