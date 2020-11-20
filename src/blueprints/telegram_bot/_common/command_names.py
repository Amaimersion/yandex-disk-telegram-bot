from enum import Enum, unique


@unique
class CommandName(Enum):
    """
    Command supported by bot.
    """
    START = "/start"
    HELP = "/help"
    ABOUT = "/about"
    SETTINGS = "/settings"
    YD_AUTH = "/grant_access"
    YD_REVOKE = "/revoke_access"
    UPLOAD_PHOTO = "/upload_photo"
    UPLOAD_FILE = "/upload_file"
    UPLOAD_AUDIO = "/upload_audio"
    UPLOAD_VIDEO = "/upload_video"
    UPLOAD_VOICE = "/upload_voice"
    UPLOAD_URL = "/upload_url"
    CREATE_FOLDER = "/create_folder"
    PUBLISH = "/publish"
    UNPUBLISH = "/unpublish"
    SPACE = "/space"
    ELEMENT_INFO = "/element_info"
