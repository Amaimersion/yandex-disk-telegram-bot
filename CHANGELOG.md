This changelog includes records about notable changes that are only visible from end user side. To see changelog from developer side, see [changelog for developers](CHANGELOG.APP.md).
___


# 1.3.1 (August 27, 2021)

Nothing changed.


# 1.3.0 (August 27, 2021)

## Added

- Ability to change default upload folder using `/settings` command.
- "Public upload by default" setting. If enabled, then when you don't specify any command in message, message content (photo, video, etc) will be uploaded and published. If disabled, then message content just will be uploaded. By default disabled.
- RU translation.
- "Report a problem" button for internal server error message.
- Automatic redirect from authorization page to the bot.

## Changed

- Changelog splitted into two files: one for end users and one for developers.
- `/disk_info`, `/space_info`: change order of information from "Used space", "Trash size", "Free space" to "Used space", "Free space", "Trash size".
- `/space_info`: text representation will be used instead of graph representation.

## Fixed

- A bug when bot sometimes could not respond of very first message of unregistered user. Such messages were a commands that require access to Yandex.Disk.


# 1.2.0 (December 14, 2020)

## Improved

- Text of some bot responses.
- Formatting of help message.
- `/upload`: multiple items will be handled at a same time, not one by one.

## Added

- `/public_upload_photo`, `/public_upload_file`, `/public_upload_audio`, `/public_upload_video`, `/public_upload_voice`, `/public_upload_url`: uploading of files and then publishing them.
- `/publish`: publishing of files or folders.
- `/unpublish`: unpublishing of files or folders.
- `/space_info`: getting of information about remaining Yandex.Disk space.
- `/element_info`: getting of information about file or folder.
- `/disk_info`: getting of information about Yandex.Disk.
- `/commands`: full list of available commands without help message.
- `/upload_url`: added `youtube-dl` support.
- Handling of files that exceed file size limit in 20 MB. At the moment the bot will asnwer with warning message, not trying to upload that file. [#3](https://github.com/Amaimersion/yandex-disk-telegram-bot/issues/3)
- Now you can forward many attachments and add single command. This command will be applied to all forwarders attachments.
- Now you can send many attachments as a one group and add single command. This command will be applied to all attachments of that group.
- Help messages for each upload command will be sended when there are no suitable input data.

## Changed

- `/create_folder`: now it will wait for folder name if you send empty command, not deny operation.
- `/upload`: on success it will return information about uploaded file, not plain status.
- `/upload`: increase maxium time of checking of operation status from 10 seconds to 16.
- `/upload_url`: result name will not contain parameters, queries and fragments.
- `/upload_voice`: result name will be ISO 8601 date, but without `T` separator (for example, `2020-11-24 09:57:46+00:00`), not ID from Telegram.

## Fixed

- `/create_folder`: fixed a bug when bot could remove `/create_folder` occurrences from folder name.
- `/create_folder`: fixed a bug when bot don't send any responses on invalid folder name.
- Wrong information in help message for `/upload_video`.
- A bug when paths with `:` in name (for example, `Telegram Bot/folder:test`) led to `DiskPathFormatError` from Yandex.


# 1.1.0 (May 9, 2020)

## Improved

- Text of most bot responses.
- Text of authorization HTML pages.
- Style of authorization HTML pages.
- When uploading, bot will update single message instead of sending new one every time with operation status.

## Added

- `/upload_url`: uploading of file using direct URL.
- Privacy Policy and Terms & Conditions.
- Favicons for different platforms.
- Buttons with useful links in `/help` command.
- "Report a problem" link in error authorization HTML page.

## Changed

- Title.
- Description.
- Logo.
- Favicon.
- Button with URL instead of plain text with URL in `/grant_access` command.

## Fixed

- A bug when sometimes "I can't track operation status of this anymore. Perform manual checking." message could appear even if operation was completed.
- A bug when empty `/create_folder` was successfully handled.


# 1.0.0 (April 15, 2020)

Initial release!
