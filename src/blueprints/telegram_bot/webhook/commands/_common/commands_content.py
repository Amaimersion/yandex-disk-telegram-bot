# flake8: noqa
# Long lines are allowed here, but try to avoid them


from flask import current_app

from src.blueprints.telegram_bot._common.command_names import CommandName


def to_code(text: str) -> str:
    return f"<code>{text}</code>"


commands_html_content = (
    {
        "name": "Yandex.Disk",
        "commands": (
            {
                "name": CommandName.UPLOAD_PHOTO.value,
                "help": (
                    "upload a photo. Original name will be "
                    "not saved, quality of photo will be decreased. "
                    "You can send photo without this command. "
                    f"Use {CommandName.PUBLIC_UPLOAD_PHOTO.value} "
                    "for public uploading"
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_PHOTO.value
            },
            {
                "name": CommandName.UPLOAD_FILE.value,
                "help": (
                    "upload a file. Original name will be saved. "
                    "For photos, original quality will be saved. "
                    "You can send file without this command. "
                    f"Use {CommandName.PUBLIC_UPLOAD_FILE.value} "
                    "for public uploading"
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_FILE.value
            },
            {
                "name": CommandName.UPLOAD_AUDIO.value,
                "help": (
                    "upload an audio. Original name will be saved, "
                    "original type may be changed. "
                    "You can send audio file without this command. "
                    f"Use {CommandName.PUBLIC_UPLOAD_AUDIO.value} "
                    "for public uploading"
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_AUDIO.value
            },
            {
                "name": CommandName.UPLOAD_VIDEO.value,
                "help": (
                    "upload a video. Original name will be saved, "
                    "original type may be changed. "
                    "You can send video file without this command. "
                    f"Use {CommandName.PUBLIC_UPLOAD_VIDEO.value} "
                    "for public uploading"
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_VIDEO.value
            },
            {
                "name": CommandName.UPLOAD_VOICE.value,
                "help": (
                    "upload a voice. "
                    "You can send voice file without this command. "
                    f"Use {CommandName.PUBLIC_UPLOAD_VOICE.value} "
                    "for public uploading"
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_VOICE.value
            },
            {
                "name": CommandName.UPLOAD_URL.value,
                "help": (
                    "upload a some resource using URL. "
                    "For direct URL's to file original name, "
                    "quality and size will be saved. "
                    "For URL's to some resource best name and "
                    "best possible quality will be selected. "
                    '"Resource" means anything: YouTube video, '
                    "Twitch clip, music track, etc. "
                    "Not everything will work as you expect, "
                    "but some URL's will. "
                    'See <a href="https://github.com/ytdl-org/youtube-dl/blob/master/docs/supportedsites.md">this</a> '
                    "for all supported sites. "
                    f"Use {CommandName.PUBLIC_UPLOAD_URL.value} "
                    "for public uploading"
                )
            },
            {
                "name": CommandName.PUBLIC_UPLOAD_URL.value
            },
            {
                "name": CommandName.PUBLISH.value,
                "help": (
                    "publish a file or folder that "
                    "already exists. Send full name of "
                    "element to publish with this command. "
                    f'Example: {to_code(f"Telegram Bot/files/photo.jpeg")}'
                )
            },
            {
                "name": CommandName.UNPUBLISH.value,
                "help": (
                    "unpublish a file or folder that "
                    "already exists. Send full name of "
                    "element to unpublish with this command. "
                    f'Example: {to_code(f"Telegram Bot/files/photo.jpeg")}'
                )
            },
            {
                "name": CommandName.CREATE_FOLDER.value,
                "help": (
                    "create a folder. Send folder name to "
                    "create with this command. Folder name "
                    "should starts from root, nested folders should be "
                    f'separated with "{to_code("/")}" character'
                )
            },
            {
                "name": CommandName.ELEMENT_INFO.value,
                "help": (
                    "get information about file or folder. "
                    "Send full path of element with this command"
                )
            },
            {
                "name": CommandName.SPACE_INFO.value,
                "help": "get information about remaining space"
            },
            {
                "name": CommandName.DISK_INFO.value,
                "help": "get information about your Yandex.Disk"
            }
        )
    },
    {
        "name": "Yandex.Disk Access",
        "commands": (
            {
                "name": CommandName.YD_AUTH.value,
                "help": "grant me access to your Yandex.Disk"
            },
            {
                "name": CommandName.YD_REVOKE.value,
                "help": "revoke my access to your Yandex.Disk"
            }
        )
    },
    {
        "name": "Settings",
        "commands": (
            {
                "name": CommandName.SETTINGS.value,
                "help": "edit your settings"
            },
        )
    },
    {
        "name": "Information",
        "commands": (
            {
                "name": CommandName.ABOUT.value,
                "help": "read about me"
            },
            {
                "name": CommandName.COMMANDS_LIST.value,
                "help": (
                    "see full list of available "
                    "commands without help message"
                )
            }
        )
    }
)
