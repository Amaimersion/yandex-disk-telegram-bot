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
    cancel_command
)
from .common.yandex_api import (
    upload_file_with_url,
    YandexAPIRequestError,
    YandexAPICreateFolderError,
    YandexAPIUploadFileError,
    YandexAPIExceededNumberOfStatusChecksError
)


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
    def message_is_valid(
        self,
        message: telegram_interface.Message
    ) -> bool:
        """
        :param message: Incoming Telegram message.

        :returns: Message is valid and should be handled.
        """
        pass

    @abstractmethod
    def get_attachment(
        self,
        message: telegram_interface.Message
    ) -> Union[dict, None]:
        """
        :param message: Incoming Telegram message.

        :returns: Attachment of message (photo object,
        file object, audio object, etc.). If `None`,
        uploading will be aborted. It must have `file_id` and
        `file_unique_id` properties. See
        https://core.telegram.org/bots/api/#available-types
        """
        pass

    @abstractmethod
    def create_file_name(
        self,
        attachment: dict,
        file: dict
    ) -> str:
        """
        :param attachment: Not `None` value from `self.get_attachment()`.
        :param file: Representation of this attachment as a file on
        Telegram servers. See https://core.telegram.org/bots/api/#file

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

        if not (self.message_is_valid(message)):
            return abort_command(chat.telegram_id)

        attachment = self.get_attachment(message)

        if (attachment is None):
            return abort_command(chat.telegram_id)

        try:
            telegram.send_chat_action(
                chat_id=chat.telegram_id,
                action=self.telegram_action
            )
        except Exception as error:
            print(error)
            return cancel_command(chat.telegram_id)

        result = None

        try:
            result = telegram.get_file(
                file_id=attachment["file_id"]
            )
        except Exception as error:
            print(error)
            return cancel_command(chat.telegram_id)

        file = result["content"]
        user_access_token = user.yandex_disk_token.get_access_token()
        folder_path = current_app.config[
            "YANDEX_DISK_API_DEFAULT_UPLOAD_FOLDER"
        ]
        file_name = self.create_file_name(attachment, file)
        download_url = telegram.create_file_download_url(
            file["file_path"]
        )

        def long_task():
            try:
                for status in upload_file_with_url(
                    access_token=user_access_token,
                    folder_path=folder_path,
                    file_name=file_name,
                    download_url=download_url
                ):
                    self.send_message(
                        chat.telegram_id,
                        f"Status: {status}"
                    )
            except YandexAPICreateFolderError as error:
                error_text = str(error) or (
                    "I can't create default upload folder "
                    "due to an unknown Yandex error."
                )

                return self.send_message(
                    chat.telegram_id,
                    error_text
                )
            except YandexAPIUploadFileError as error:
                error_text = str(error) or (
                    "I can't upload this due "
                    "to an unknown Yandex error."
                )

                return self.send_message(
                    chat.telegram_id,
                    error_text
                )
            except YandexAPIExceededNumberOfStatusChecksError:
                error_text = (
                    "I can't track operation status of "
                    "this anymore. Perform manual checking."
                )

                return self.send_message(
                    chat.telegram_id,
                    error_text
                )
            except (YandexAPIRequestError, Exception) as error:
                print(error)
                sended_message_id = None

                if (self.sended_message is not None):
                    sended_message_id = self.sended_message.message_id

                return cancel_command(
                    chat.telegram_id,
                    sended_message_id
                )

        long_task()

    def send_message(self, chat_id: int, text: str) -> None:
        """
        Sends message to Telegram user.

        - if message already was sent, then sent message
        will be updated with new text.
        """
        if (self.sended_message is None):
            result = telegram.send_message(
                chat_id=chat_id,
                text=text
            )
            self.sended_message = telegram_interface.Message(
                result["content"]
            )
        else:
            telegram.edit_message_text(
                chat_id=chat_id,
                message_id=self.sended_message.message_id,
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

    def message_is_valid(self, message: telegram_interface.Message):
        raw_data = message.raw_data

        return (
            isinstance(
                raw_data.get("photo"),
                list
            ) and
            len(raw_data["photo"]) > 0
        )

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

    def message_is_valid(self, message: telegram_interface.Message):
        return (
            isinstance(
                message.raw_data.get("document"),
                dict
            )
        )

    def get_attachment(self, message: telegram_interface.Message):
        return message.raw_data["document"]

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

    def message_is_valid(self, message: telegram_interface.Message):
        return (
            isinstance(
                message.raw_data.get("audio"),
                dict
            )
        )

    def get_attachment(self, message: telegram_interface.Message):
        return message.raw_data["audio"]

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

    def message_is_valid(self, message: telegram_interface.Message):
        return (
            isinstance(
                message.raw_data.get("video"),
                dict
            )
        )

    def get_attachment(self, message: telegram_interface.Message):
        return message.raw_data["video"]

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

    def message_is_valid(self, message: telegram_interface.Message):
        return (
            isinstance(
                message.raw_data.get("voice"),
                dict
            )
        )

    def get_attachment(self, message: telegram_interface.Message):
        return message.raw_data["voice"]

    def create_file_name(self, attachment, file):
        name = file["file_unique_id"]

        if ("mime_type" in attachment):
            types = attachment["mime_type"].split("/")
            extension = types[1]
            name = f"{name}.{extension}"

        return name


handle_photo = PhotoHandler.handle
handle_file = FileHandler.handle
handle_audio = AudioHandler.handle
handle_video = VideoHandler.handle
handle_voice = VoiceHandler.handle
