from abc import ABCMeta, abstractmethod
from typing import Union

from flask import g, current_app

from src.api import telegram
from src.blueprints.telegram_bot.webhook import telegram_interface
from .common.decorators import (
    yd_access_token_required,
    get_db_data
)
from .common.responses import (
    abort_command,
    cancel_command,
    AbortReason
)
from .common.yandex_api import (
    upload_file_with_url,
    YandexAPIRequestError,
    YandexAPICreateFolderError,
    YandexAPIUploadFileError,
    YandexAPIExceededNumberOfStatusChecksError
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
        :param ok: Message is valid for subsequent handling.
        :param abort_reason: Reason of abort. `None` if `ok = True`.
        """
        self.ok = ok
        self.abort_reason = None


class AttachmentHandler(metaclass=ABCMeta):
    """
    Handles uploading of attachment of Telegram message.
    """
    def __init__(self) -> None:
        # Sended message to Telegram user.
        # This message will be updated, rather
        # than sending new message every time
        self.sended_message: Union[
            telegram_interface.Message,
            None
        ] = None

    @staticmethod
    @abstractmethod
    def handle() -> None:
        """
        Starts uploading process.
        """
        pass

    @property
    @abstractmethod
    def telegram_action(self) -> str:
        """
        :returns: Action type from
        https://core.telegram.org/bots/api/#sendchataction
        """
        pass

    @abstractmethod
    def check_message_health(
        self,
        message: telegram_interface.Message
    ) -> MessageHealth:
        """
        :param message: Incoming Telegram message.

        :returns: See `MessageHealth` documentation.
        Message will be handled by next operators only
        in case of `ok = true`.
        """
        pass

    @abstractmethod
    def get_attachment(
        self,
        message: telegram_interface.Message
    ) -> Union[dict, str, None]:
        """
        :param message: Incoming Telegram message.

        :returns: Attachment of message (photo object,
        file object, audio object, etc.). If `None`,
        uploading will be aborted. If `dict`, it must have `file_id`
        and `file_unique_id` properties. If `str`, it is assumed
        as direct file URL. See
        https://core.telegram.org/bots/api/#available-types
        """
        pass

    @abstractmethod
    def create_file_name(
        self,
        attachment: Union[dict, str],
        file: Union[dict, None]
    ) -> str:
        """
        :param attachment: Not `None` value from `self.get_attachment()`.
        :param file: Representation of this attachment as a file on
        Telegram servers. If `attachment` is `str`, then this will
        be equal `None`. See https://core.telegram.org/bots/api/#file

        :returns: Name of file which will be uploaded.
        """
        pass

    @yd_access_token_required
    @get_db_data
    def upload(self) -> None:
        """
        Uploads an attachment.
        """
        message = g.telegram_message
        user = g.db_user
        chat = g.db_chat
        message_health = self.check_message_health(message)

        if not (message_health.ok):
            return abort_command(
                chat.telegram_id,
                message_health.abort_reason or AbortReason.UNKNOWN
            )

        attachment = self.get_attachment(message)

        if (attachment is None):
            return abort_command(
                chat.telegram_id,
                AbortReason.NO_SUITABLE_DATA
            )

        try:
            telegram.send_chat_action(
                chat_id=chat.telegram_id,
                action=self.telegram_action
            )
        except Exception as error:
            print(error)
            return cancel_command(chat.telegram_id)

        download_url = None
        file = None

        if (isinstance(attachment, str)):
            download_url = attachment
        else:
            result = None

            try:
                result = telegram.get_file(
                    file_id=attachment["file_id"]
                )
            except Exception as error:
                print(error)
                return cancel_command(chat.telegram_id)

            file = result["content"]
            download_url = telegram.create_file_download_url(
                file["file_path"]
            )

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
                    self.send_message(f"Status: {status}")
            except YandexAPICreateFolderError as error:
                error_text = str(error) or (
                    "I can't create default upload folder "
                    "due to an unknown Yandex error."
                )

                return self.send_message(error_text)
            except YandexAPIUploadFileError as error:
                error_text = str(error) or (
                    "I can't upload this due "
                    "to an unknown Yandex error."
                )

                return self.send_message(error_text)
            except YandexAPIExceededNumberOfStatusChecksError:
                error_text = (
                    "I can't track operation status of "
                    "this anymore. Perform manual checking."
                )

                return self.send_message(error_text)
            except (YandexAPIRequestError, Exception) as error:
                print(error)

                if (self.sended_message is None):
                    return cancel_command(
                        chat.telegram_id,
                        reply_to_message=message.message_id
                    )
                else:
                    return cancel_command(
                        chat.telegram_id,
                        edit_message=self.sended_message.message_id
                    )

        long_task()

    def send_message(self, text: str) -> None:
        """
        Sends message to Telegram user.

        - if message already was sent, then sent message
        will be updated with new text.
        """
        incoming_message = g.telegram_message
        chat = g.db_chat

        if (self.sended_message is None):
            result = telegram.send_message(
                reply_to_message_id=incoming_message.message_id,
                chat_id=chat.telegram_id,
                text=text
            )
            self.sended_message = telegram_interface.Message(
                result["content"]
            )
        elif (text != self.sended_message.get_text()):
            telegram.edit_message_text(
                message_id=self.sended_message.message_id,
                chat_id=chat.telegram_id,
                text=text
            )


class PhotoHandler(AttachmentHandler):
    """
    Handles uploading of photo.
    """
    @staticmethod
    def handle():
        handler = PhotoHandler()
        handler.upload()

    @property
    def telegram_action(self):
        return "upload_photo"

    def check_message_health(self, message: telegram_interface.Message):
        health = MessageHealth(True)
        raw_data = message.raw_data

        if not (
            isinstance(
                raw_data.get("photo"),
                list
            ) and
            len(raw_data["photo"]) > 0
        ):
            health.ok = False
            health.abort_reason = AbortReason.NO_SUITABLE_DATA

        return health

    def get_attachment(self, message: telegram_interface.Message):
        raw_data = message.raw_data
        photos = raw_data["photo"]
        biggest_photo = photos[0]

        for photo in photos[1:]:
            if (photo["height"] > biggest_photo["height"]):
                biggest_photo = photo

        return biggest_photo

    def create_file_name(self, attachment, file):
        return file["file_unique_id"]


class FileHandler(AttachmentHandler):
    """
    Handles uploading of file.
    """
    @staticmethod
    def handle():
        handler = FileHandler()
        handler.upload()

    @property
    def telegram_action(self):
        return "upload_document"

    def check_message_health(self, message: telegram_interface.Message):
        health = MessageHealth(True)
        value = self.get_attachment(message)

        if not (
            isinstance(value, dict)
        ):
            health.ok = False
            health.abort_reason = AbortReason.NO_SUITABLE_DATA

        return health

    def get_attachment(self, message: telegram_interface.Message):
        return message.raw_data.get("document")

    def create_file_name(self, attachment, file):
        return (
            attachment.get("file_name") or
            file["file_unique_id"]
        )


class AudioHandler(AttachmentHandler):
    """
    Handles uploading of audio.
    """
    @staticmethod
    def handle():
        handler = AudioHandler()
        handler.upload()

    @property
    def telegram_action(self):
        return "upload_audio"

    def check_message_health(self, message: telegram_interface.Message):
        health = MessageHealth(True)
        value = self.get_attachment(message)

        if not (
            isinstance(value, dict)
        ):
            health.ok = False
            health.abort_reason = AbortReason.NO_SUITABLE_DATA

        return health

    def get_attachment(self, message: telegram_interface.Message):
        return message.raw_data.get("audio")

    def create_file_name(self, attachment, file):
        name = file["file_unique_id"]

        if ("title" in attachment):
            name = attachment["title"]

        if ("performer" in attachment):
            name = f"{attachment['performer']} - {name}"

        if ("mime_type" in attachment):
            types = attachment["mime_type"].split("/")
            extension = types[1]
            name = f"{name}.{extension}"

        return name


class VideoHandler(AttachmentHandler):
    """
    Handles uploading of video.
    """
    @staticmethod
    def handle():
        handler = VideoHandler()
        handler.upload()

    @property
    def telegram_action(self):
        return "upload_video"

    def check_message_health(self, message: telegram_interface.Message):
        health = MessageHealth(True)
        value = self.get_attachment(message)

        if not (
            isinstance(value, dict)
        ):
            health.ok = False
            health.abort_reason = AbortReason.NO_SUITABLE_DATA

        return health

    def get_attachment(self, message: telegram_interface.Message):
        return message.raw_data.get("video")

    def create_file_name(self, attachment, file):
        name = file["file_unique_id"]

        if ("mime_type" in attachment):
            types = attachment["mime_type"].split("/")
            extension = types[1]
            name = f"{name}.{extension}"

        return name


class VoiceHandler(AttachmentHandler):
    """
    Handles uploading of voice.
    """
    @staticmethod
    def handle():
        handler = VoiceHandler()
        handler.upload()

    @property
    def telegram_action(self):
        return "upload_audio"

    def check_message_health(self, message: telegram_interface.Message):
        health = MessageHealth(True)
        value = self.get_attachment(message)

        if not (
            isinstance(value, dict)
        ):
            health.ok = False
            health.abort_reason = AbortReason.NO_SUITABLE_DATA

        return health

    def get_attachment(self, message: telegram_interface.Message):
        return message.raw_data.get("voice")

    def create_file_name(self, attachment, file):
        name = file["file_unique_id"]

        if ("mime_type" in attachment):
            types = attachment["mime_type"].split("/")
            extension = types[1]
            name = f"{name}.{extension}"

        return name


class URLHandler(AttachmentHandler):
    """
    Handles uploading of direct URL to file.
    """
    @staticmethod
    def handle():
        handler = URLHandler()
        handler.upload()

    @property
    def telegram_action(self):
        return "upload_document"

    def check_message_health(self, message: telegram_interface.Message):
        health = MessageHealth(True)
        value = self.get_attachment(message)

        if not (
            isinstance(value, str) and
            len(value) > 0
        ):
            health.ok = False
            health.abort_reason = AbortReason.NO_SUITABLE_DATA

        return health

    def get_attachment(self, message: telegram_interface.Message):
        return message.get_entity_value("url")

    def create_file_name(self, attachment, file):
        return attachment.split("/")[-1]


handle_photo = PhotoHandler.handle
handle_file = FileHandler.handle
handle_audio = AudioHandler.handle
handle_video = VideoHandler.handle
handle_voice = VoiceHandler.handle
handle_url = URLHandler.handle
