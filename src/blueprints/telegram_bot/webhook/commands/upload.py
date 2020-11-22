from abc import ABCMeta, abstractmethod
from typing import Union

from flask import g, current_app

from src.api import telegram
from src.blueprints.telegram_bot._common.telegram_interface import (
    Message as TelegramMessage
)
from src.blueprints.telegram_bot._common.command_names import (
    CommandName
)
from src.blueprints.telegram_bot._common.yandex_disk import (
    upload_file_with_url,
    get_element_info,
    YandexAPIRequestError,
    YandexAPICreateFolderError,
    YandexAPIUploadFileError,
    YandexAPIExceededNumberOfStatusChecksError
)
from ._common.decorators import (
    yd_access_token_required,
    get_db_data
)
from ._common.responses import (
    abort_command,
    cancel_command,
    send_yandex_disk_error,
    AbortReason
)
from ._common.utils import (
    create_element_info_html_text
)


class MessageHealth:
    """
    Health status of Telegram message.
    """
    def __init__(
        self,
        ok: bool,
        abort_reason: Union[AbortReason, None] = None
    ) -> None:
        """
        :param ok:
        Message is valid for subsequent handling.
        :param abort_reason:
        Reason of abort. `None` if `ok = True`.
        """
        self.ok = ok
        self.abort_reason = None


class AttachmentHandler(metaclass=ABCMeta):
    """
    Handles uploading of attachment of Telegram message.

    - most of attachments will be treated as files.
    - some of the not abstract class functions are common
    for most attachments. If you need specific logic in some
    function, then override it.
    """
    def __init__(self) -> None:
        # Sended message to Telegram user.
        # This message will be updated, instead
        # than sending new message every time again
        self.sended_message: Union[TelegramMessage, None] = None

    @staticmethod
    @abstractmethod
    def handle(*args, **kwargs) -> None:
        """
        Starts uploading process.

        - `*args`, `**kwargs` - arguments from dispatcher.

        :raises:
        Raises an error if any! So, this function should
        be handled by top-function.
        """
        pass

    @property
    @abstractmethod
    def telegram_action(self) -> str:
        """
        :returns:
        Action type from
        https://core.telegram.org/bots/api/#sendchataction
        """
        pass

    @property
    @abstractmethod
    def raw_data_key(self) -> str:
        """
        :returns:
        Key in message, under this key stored needed raw data.
        Example: `audio`.
        See https://core.telegram.org/bots/api#message
        """
        pass

    @property
    @abstractmethod
    def raw_data_type(self) -> type:
        """
        :returns:
        Expected type of raw data.
        Example: `dict`.
        `None` never should be returned!
        """
        pass

    @abstractmethod
    def create_help_message(self) -> str:
        """
        - supports HTML markup.

        :returns:
        Help message that will be sended to user
        in case of some triggers (for example, when
        there are no suitable data for handling).
        """
        pass

    def get_attachment(
        self,
        message: TelegramMessage
    ) -> Union[dict, str, None]:
        """
        :param message:
        Incoming Telegram message.

        :returns:
        Attachment of message (photo object, file object,
        audio object, etc.). If `None`, then uploading should
        be aborted. If `dict`, it will have `file_id` and
        `file_unique_id` properties. If `str`, it should be
        assumed as direct file URL.
        See https://core.telegram.org/bots/api/#available-types
        """
        return message.raw_data.get(self.raw_data_key)

    def check_message_health(
        self,
        message: TelegramMessage
    ) -> MessageHealth:
        """
        :param message:
        Incoming Telegram message.

        :returns:
        See `MessageHealth` documentation.
        Message should be handled by next operators only
        in case of `ok = true`.
        """
        health = MessageHealth(True)
        value = self.get_attachment(message)

        if not isinstance(value, self.raw_data_type):
            health.ok = False
            health.abort_reason = AbortReason.NO_SUITABLE_DATA
        elif (
            (type(value) in [str]) and
            (len(value) == 0)
        ):
            health.ok = False
            health.abort_reason = AbortReason.NO_SUITABLE_DATA
        elif (
            isinstance(value, dict) and
            self.is_too_big_file(value)
        ):
            health.ok = False
            health.abort_reason = AbortReason.EXCEED_FILE_SIZE_LIMIT

        return health

    def create_file_name(
        self,
        attachment: Union[dict, str],
        file: Union[dict, None]
    ) -> str:
        """
        :param attachment:
        Not `None` value from `self.get_attachment()`.
        :param file:
        Representation of this attachment as a file on
        Telegram servers. If `attachment` is `str`, then
        this will be equal `None`.
        See https://core.telegram.org/bots/api/#file

        :returns:
        Name of file which will be uploaded.
        """
        if isinstance(attachment, str):
            return attachment

        name = (
            attachment.get("file_name") or
            file["file_unique_id"]
        )
        extension = self.get_mime_type(attachment)

        if extension:
            name = f"{name}.{extension}"

        return name

    def get_mime_type(self, attachment: dict) -> str:
        """
        :param attachment:
        `dict` result from `self.get_attachment()`.

        :returns:
        Empty string in case if `attachment` doesn't have
        required key. Otherwise mime type of this attachment.
        """
        result = ""

        if "mime_type" in attachment:
            types = attachment["mime_type"].split("/")
            result = types[1]

        return result

    def is_too_big_file(self, file: dict) -> bool:
        """
        Checks if size of file exceeds limit size of upload.

        :param file:
        `dict` value from `self.get_attachment()`.

        :returns:
        File size exceeds upload limit size.
        Always `False` if file size is unknown.
        """
        limit = current_app.config["TELEGRAM_API_MAX_FILE_SIZE"]
        size = limit

        if "file_size" in file:
            size = file["file_size"]

        return (size > limit)

    @yd_access_token_required
    @get_db_data
    def upload(self, *args, **kwargs) -> None:
        """
        Uploads an attachment.

        `*args`, `**kwargs` - arguments from dispatcher.
        """
        chat_id = kwargs.get(
            "chat_id",
            g.db_chat.telegram_id
        )
        message = kwargs.get(
            "message",
            g.telegram_message
        )
        message_health = self.check_message_health(message)

        if not message_health.ok:
            reason = (
                message_health.abort_reason or
                AbortReason.UNKNOWN
            )

            if (reason == AbortReason.NO_SUITABLE_DATA):
                return self.send_html_message(
                    chat_id,
                    self.create_help_message()
                )
            else:
                return abort_command(chat_id, reason)

        attachment = self.get_attachment(message)
        data_is_empty = (attachment is None)

        if data_is_empty:
            return self.send_html_message(
                chat_id,
                self.create_help_message()
            )

        try:
            telegram.send_chat_action(
                chat_id=chat_id,
                action=self.telegram_action
            )
        except Exception as error:
            cancel_command(chat_id)
            raise error

        download_url = None
        file = None

        if isinstance(attachment, str):
            download_url = attachment
        else:
            result = None

            try:
                result = telegram.get_file(
                    file_id=attachment["file_id"]
                )
            except Exception as error:
                cancel_command(chat_id)
                raise error

            file = result["content"]
            download_url = telegram.create_file_download_url(
                file["file_path"]
            )

        user = g.db_user
        file_name = self.create_file_name(attachment, file)
        user_access_token = user.yandex_disk_token.get_access_token()
        folder_path = current_app.config[
            "YANDEX_DISK_API_DEFAULT_UPLOAD_FOLDER"
        ]

        def long_task():
            try:
                for status in upload_file_with_url(
                    user_access_token=user_access_token,
                    folder_path=folder_path,
                    file_name=file_name,
                    download_url=download_url
                ):
                    success = status["success"]
                    text = ""
                    is_html_text = False

                    if success:
                        info = None
                        full_path = f"{folder_path}/{file_name}"

                        try:
                            info = get_element_info(
                                user_access_token,
                                full_path,
                                get_public_info=False
                            )
                        except Exception:
                            pass

                        if info:
                            text = create_element_info_html_text(
                                info,
                                include_private_info=True
                            )
                            is_html_text = True
                        else:
                            text = (
                                "Successfully completed, but failed "
                                "to get information about this file."
                                "\n"
                                "Type to see information:"
                                "\n"
                                f"{CommandName.ELEMENT_INFO.value} {full_path}"
                            )
                    else:
                        # You shouldn't use HTML for this,
                        # because `upload_status` can be a same
                        upload_status = status["status"]
                        text = f"Status: {upload_status}"

                    self.reply_to_message(
                        message.message_id,
                        chat_id,
                        text,
                        is_html_text
                    )
            except YandexAPICreateFolderError as error:
                error_text = str(error) or (
                    "I can't create default upload folder "
                    "due to an unknown Yandex.Disk error."
                )

                return send_yandex_disk_error(
                    chat_id,
                    error_text,
                    message.message_id
                )
            except YandexAPIUploadFileError as error:
                error_text = str(error) or (
                    "I can't upload this due "
                    "to an unknown Yandex.Disk error."
                )

                return send_yandex_disk_error(
                    chat_id,
                    error_text,
                    message.message_id
                )
            except YandexAPIExceededNumberOfStatusChecksError:
                error_text = (
                    "I can't track operation status of "
                    "this anymore. Perform manual checking."
                )

                return self.reply_to_message(
                    message.message_id,
                    chat_id,
                    error_text
                )
            except Exception as error:
                if self.sended_message is None:
                    cancel_command(
                        chat_id,
                        reply_to_message=message.message_id
                    )
                else:
                    cancel_command(
                        chat_id,
                        edit_message=self.sended_message.message_id
                    )

                raise error

        long_task()

    def send_html_message(
        self,
        chat_id: int,
        html_text: str
    ) -> None:
        """
        Sends HTML message to Telegram user.
        """
        telegram.send_message(
            chat_id=chat_id,
            text=html_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    def reply_to_message(
        self,
        incoming_message_id: int,
        chat_id: int,
        text: str,
        html_text=False
    ) -> None:
        """
        Sends reply message to Telegram user.

        - if message already was sent, then sent
        message will be updated with new text.
        - NOTE: using HTML text may lead to error,
        because text should be compared with already
        sended text, but already sended text will not
        contain HTML tags (even if they was before sending),
        and `text` will, so, comparing already sended HTML
        text and `text` always will results to `False`.
        """
        enabled_html = {}

        if html_text:
            enabled_html["parse_mode"] = "HTML"

        if self.sended_message is None:
            result = telegram.send_message(
                reply_to_message_id=incoming_message_id,
                chat_id=chat_id,
                text=text,
                allow_sending_without_reply=True,
                disable_web_page_preview=True,
                **enabled_html
            )
            self.sended_message = TelegramMessage(
                result["content"]
            )
        elif (text != self.sended_message.get_text()):
            telegram.edit_message_text(
                message_id=self.sended_message.message_id,
                chat_id=chat_id,
                text=text,
                disable_web_page_preview=True,
                **enabled_html
            )


class PhotoHandler(AttachmentHandler):
    """
    Handles uploading of photo.
    """
    @staticmethod
    def handle(*args, **kwargs):
        handler = PhotoHandler()
        handler.upload(*args, **kwargs)

    @property
    def telegram_action(self):
        return "upload_photo"

    @property
    def raw_data_key(self):
        return "photo"

    @property
    def raw_data_type(self):
        # dict, not list, because we will select biggest photo
        return dict

    def create_help_message(self):
        return (
            "Send a photos that you want to upload."
            "\n\n"
            "Note:"
            "\n"
            "- original name will be not saved"
            "\n"
            "- original quality and size will be decreased"
        )

    def get_attachment(self, message: TelegramMessage):
        photos = message.raw_data.get(self.raw_data_key, [])
        biggest_photo = None
        biggest_pixels_count = -1

        for photo in photos:
            if self.is_too_big_file(photo):
                continue

            current_pixels_count = photo["width"] * photo["height"]

            if (current_pixels_count > biggest_pixels_count):
                biggest_photo = photo
                biggest_pixels_count = current_pixels_count

        return biggest_photo


class FileHandler(AttachmentHandler):
    """
    Handles uploading of file.
    """
    @staticmethod
    def handle(*args, **kwargs):
        handler = FileHandler()
        handler.upload(*args, **kwargs)

    @property
    def telegram_action(self):
        return "upload_document"

    @property
    def raw_data_key(self):
        return "document"

    @property
    def raw_data_type(self):
        return dict

    def create_help_message(self):
        return (
            "Send a files that you want to upload."
            "\n\n"
            "Note:"
            "\n"
            "- original name will be saved"
            "\n"
            "- original quality and size will be saved"
        )

    def get_mime_type(self, attachment):
        # file name already contains type
        return ""


class AudioHandler(AttachmentHandler):
    """
    Handles uploading of audio.
    """
    @staticmethod
    def handle(*args, **kwargs):
        handler = AudioHandler()
        handler.upload(*args, **kwargs)

    @property
    def telegram_action(self):
        return "upload_audio"

    @property
    def raw_data_key(self):
        return "audio"

    @property
    def raw_data_type(self):
        return dict

    def create_help_message(self):
        return (
            "Send a music that you want to upload."
            "\n\n"
            "Note:"
            "\n"
            "- original name will be saved"
            "\n"
            "- original quality and size will be saved"
            "\n"
            "- original type may be changed"
        )

    def create_file_name(self, attachment, file):
        name = file["file_unique_id"]

        if "title" in attachment:
            name = attachment["title"]

        if "performer" in attachment:
            name = f"{attachment['performer']} - {name}"

        extension = self.get_mime_type(attachment)

        if extension:
            name = f"{name}.{extension}"

        return name


class VideoHandler(AttachmentHandler):
    """
    Handles uploading of video.
    """
    @staticmethod
    def handle(*args, **kwargs):
        handler = VideoHandler()
        handler.upload(*args, **kwargs)

    @property
    def telegram_action(self):
        return "upload_video"

    @property
    def raw_data_key(self):
        return "video"

    @property
    def raw_data_type(self):
        return dict

    def create_help_message(self):
        return (
            "Send a video that you want to upload."
            "\n\n"
            "Note:"
            "\n"
            "- original name will be saved"
            "\n"
            "- original quality and size will be saved"
            "\n"
            "- original type may be changed"
        )


class VoiceHandler(AttachmentHandler):
    """
    Handles uploading of voice.
    """
    @staticmethod
    def handle(*args, **kwargs):
        handler = VoiceHandler()
        handler.upload(*args, **kwargs)

    @property
    def telegram_action(self):
        return "upload_audio"

    @property
    def raw_data_key(self):
        return "voice"

    @property
    def raw_data_type(self):
        return dict

    def create_help_message(self):
        return (
            "Send a voice message that you want to upload."
        )


class URLHandler(AttachmentHandler):
    """
    Handles uploading of direct URL to file.
    """
    @staticmethod
    def handle(*args, **kwargs):
        handler = URLHandler()
        handler.upload(*args, **kwargs)

    @property
    def telegram_action(self):
        return "upload_document"

    @property
    def raw_data_key(self):
        return "url"

    @property
    def raw_data_type(self):
        return str

    def create_help_message(self):
        return (
            "Send a direct URL to file that you want to upload."
            "\n\n"
            "Note:"
            "\n"
            "- original name from URL will be saved"
            "\n"
            "- original quality and size will be saved"
        )

    def get_attachment(self, message: TelegramMessage):
        return message.get_entity_value(self.raw_data_key)

    def create_file_name(self, attachment, file):
        return attachment.split("/")[-1]


handle_photo = PhotoHandler.handle
handle_file = FileHandler.handle
handle_audio = AudioHandler.handle
handle_video = VideoHandler.handle
handle_voice = VoiceHandler.handle
handle_url = URLHandler.handle
