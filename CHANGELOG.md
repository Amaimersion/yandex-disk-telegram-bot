# 1.2.0

## Telegram Bot

### Added

- `/publish`: publishing of files or folders.
- Handling of files that exceed file size limit in 20 MB. At the moment the bot will asnwer with warning message, not trying to upload that file. [#3](https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/3)

## Project

### Improved

- Upgrade `python` to 3.8.2.

### Changed

- Redirect to favicon will be handled by nginx.
- Biggest photo (from single photo file) will be selected based on total pixels count, not based on height.


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
