from enum import Enum, unique
from typing import Union


@unique
class CommandName(Enum):
    """
    Command supported by bot.

    - in most cases you should use value of enum variable
    directly, because it is actual command name. But if
    you want to use short identificator (for callback query
    data, for example), then you can get int ID of enum
    variable using `get_index()`.
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

    @staticmethod
    def values():
        return [i.value for i in CommandName]

    @staticmethod
    def get_index(name: str) -> Union[int, None]:
        """
        NOTE:
        you shouldn't rely on index order!

        :returns:
        Index of that enum name.
        `None` if name is unknown.
        """
        values = CommandName.values()

        for i in range(len(values)):
            if (values[i] == name):
                return i

        return None

    @staticmethod
    def get_name(index: int) -> Union[str, None]:
        """
        :returns:
        Enum variable name.
        `None` if index is outside of values array.

        :raises:
        In case if index is negative.
        """
        if (index < 0):
            raise Exception("Negative index is not supported")

        values = CommandName.values()

        if (index >= len(values)):
            return None

        return values[index]
