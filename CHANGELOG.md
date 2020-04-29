# 1.1.0

## Telegram Bot

### Improved

- Text of most bot responses.
- When uploading, bot will update single message instead of sending new one every time with operation status.

### Added

- Privacy Policy and Terms & Conditions.
- Favicons for different platforms.
- Buttons with useful links in `/help` command.

### Changed

- Title.
- Description.
- Logo.
- Favicon.
- Button with URL instead of plain text with URL in `/grant_access` command.

## Project

### Improved

- Big refactoring of everything.
- File structure.

### Added

- `SERVER_NAME` environment variable.

### Changed

- Decreased size of slug on Heroku by removing unused files and folders.
- Decreased number of seconds for Yandex.OAuth request timeout.
- Redirects and generated URL's always will be absolute URL's with `PREFERRED_URL_SCHEME + SERVER_NAME`.


# 1.0.0 (April 15, 2020)

Initial release!
