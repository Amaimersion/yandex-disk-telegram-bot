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
    PUBLIC_UPLOAD_PHOTO = "/public_upload_photo"
    PUBLIC_UPLOAD_FILE = "/public_upload_file"
    PUBLIC_UPLOAD_AUDIO = "/public_upload_audio"
    PUBLIC_UPLOAD_VIDEO = "/public_upload_video"
    PUBLIC_UPLOAD_VOICE = "/public_upload_voice"
    PUBLIC_UPLOAD_URL = "/public_upload_url"
    CREATE_FOLDER = "/create_folder"
    PUBLISH = "/publish"
    UNPUBLISH = "/unpublish"
    SPACE_INFO = "/space_info"
    ELEMENT_INFO = "/element_info"
    DISK_INFO = "/disk_info"
    COMMANDS_LIST = "/commands"
