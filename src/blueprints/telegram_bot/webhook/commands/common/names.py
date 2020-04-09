from enum import Enum, unique


@unique
class CommandNames(Enum):
    """
    Commands supported by bot.
    """
    START = "/start"
    HELP = "/help"
    ABOUT = "/about"
    SETTINGS = "/settings"
    YD_AUTH = "/yandex_disk_authorization"
    YD_REVOKE = "/yandex_disk_revoke"
    UPLOAD_PHOTO = "/upload_photo"
    UPLOAD_FILE = "/upload_file"
    UPLOAD_AUDIO = "/upload_audio"
    UPLOAD_VIDEO = "/upload_video"
    UPLOAD_VOICE = "/upload_voice"
    CREATE_FOLDER = "/create_folder"
