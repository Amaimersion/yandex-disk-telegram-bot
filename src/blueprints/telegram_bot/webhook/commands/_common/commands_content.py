# flake8: noqa
# Long lines are allowed here, but try to avoid them


from flask import current_app

from src.i18n import lazy_gettext
from src.blueprints.telegram_bot._common.command_names import CommandName


def to_code(text: str) -> str:
    return f"<code>{text}</code>"


url = {
    "ytdl-supportedsites": "https://github.com/ytdl-org/youtube-dl/blob/master/docs/supportedsites.md"
}
commands_html_content = (
    {
        "name": lazy_gettext("Yandex.Disk"),
        "commands": (
            {
                "name": CommandName.UPLOAD_PHOTO.value,
                "help": lazy_gettext(
                    "upload a photo. Original name will be "
                    "not saved, quality of photo will be decreased. "
                    "You can send photo without this command. "
                    "Use %(public_upload_command)s for public uploading",
                    public_upload_command=CommandName.PUBLIC_UPLOAD_PHOTO.value
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_PHOTO.value
            },
            {
                "name": CommandName.UPLOAD_FILE.value,
                "help": lazy_gettext(
                    "upload a file. Original name will be saved. "
                    "For photos, original quality will be saved. "
                    "You can send file without this command. "
                    "Use %(public_upload_command)s for public uploading",
                    public_upload_command=CommandName.PUBLIC_UPLOAD_FILE.value
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_FILE.value
            },
            {
                "name": CommandName.UPLOAD_AUDIO.value,
                "help": lazy_gettext(
                    "upload an audio. Original name will be saved, "
                    "original type may be changed. "
                    "You can send audio file without this command. "
                    "Use %(public_upload_command)s for public uploading",
                    public_upload_command=CommandName.PUBLIC_UPLOAD_AUDIO.value
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_AUDIO.value
            },
            {
                "name": CommandName.UPLOAD_VIDEO.value,
                "help": lazy_gettext(
                    "upload a video. Original name will be saved, "
                    "original type may be changed. "
                    "You can send video file without this command. "
                    "Use %(public_upload_command)s for public uploading",
                    public_upload_command=CommandName.PUBLIC_UPLOAD_VIDEO.value
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_VIDEO.value
            },
            {
                "name": CommandName.UPLOAD_VOICE.value,
                "help": lazy_gettext(
                    "upload a voice. "
                    "You can send voice file without this command. "
                    "Use %(public_upload_command)s for public uploading",
                    public_upload_command=CommandName.PUBLIC_UPLOAD_VOICE.value
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_VOICE.value
            },
            {
                "name": CommandName.UPLOAD_URL.value,
                "help": lazy_gettext(
                    "upload a some resource using URL. "
                    "For direct URL's to file original name, "
                    "quality and size will be saved. "
                    "For URL's to some resource best name and "
                    "best possible quality will be selected. "
                    '"Resource" means anything: YouTube video, '
                    "Twitch clip, music track, etc. "
                    "Not everything will work as you expect, "
                    "but some URL's will. "
                    'See <a href="%(ytdl_url)s">this</a> for all supported sites. '
                    "Use %(public_upload_command)s for public uploading",
                    public_upload_command=CommandName.PUBLIC_UPLOAD_URL.value,
                    ytdl_url=url["ytdl-supportedsites"]
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_URL.value
            },
            {
                "name": CommandName.PUBLISH.value,
                "help": lazy_gettext(
                    "publish a file or folder that "
                    "already exists. Send full name of "
                    "element to publish with this command. "
                    'Example: %(example)s',
                    example=to_code("Telegram Bot/files/photo.jpeg")
                )
            },
            {
                "name": CommandName.UNPUBLISH.value,
                "help": lazy_gettext(
                    "unpublish a file or folder that "
                    "already exists. Send full name of "
                    "element to unpublish with this command. "
                    'Example: %(example)s',
                    example=to_code("Telegram Bot/files/photo.jpeg")
                )
            },
            {
                "name": CommandName.CREATE_FOLDER.value,
                "help": lazy_gettext(
                    "create a folder. Send folder name to "
                    "create with this command. Folder name "
                    "should starts from root, nested folders should be "
                    'separated with "%(separator)s" character',
                    separator=to_code("/")
                )
            },
            {
                "name": CommandName.ELEMENT_INFO.value,
                "help": lazy_gettext(
                    "get information about file or folder. "
                    "Send full path of element with this command"
                )
            },
            {
                "name": CommandName.SPACE_INFO.value,
                "help": lazy_gettext(
                    "get information about remaining space"
                )
            },
            {
                "name": CommandName.DISK_INFO.value,
                "help": lazy_gettext(
                    "get information about your Yandex.Disk"
                )
            }
        )
    },
    {
        "name": "Yandex.Disk Access",
        "commands": (
            {
                "name": CommandName.YD_AUTH.value,
                "help": lazy_gettext(
                    "grant me access to your Yandex.Disk"
                )
            },
            {
                "name": CommandName.YD_REVOKE.value,
                "help": lazy_gettext(
                    "revoke my access to your Yandex.Disk"
                )
            }
        )
    },
    {
        "name": "Settings",
        "commands": (
            {
                "name": CommandName.SETTINGS.value,
                "help": lazy_gettext(
                    "edit your settings"
                )
            },
        )
    },
    {
        "name": "Information",
        "commands": (
            {
                "name": CommandName.ABOUT.value,
                "help": lazy_gettext(
                    "read about me"
                )
            },
            {
                "name": CommandName.COMMANDS_LIST.value,
                "help": lazy_gettext(
                    "see full list of available "
                    "commands without help message"
                )
            }
        )
    }
)
