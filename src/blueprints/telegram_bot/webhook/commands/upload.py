from abc import ABCMeta, abstractmethod
from typing import Union

from flask import g, current_app

from .....api import telegram
from .....concurrent import executor
from .common.decorators import (
    yd_access_token_required,
    get_db_data
)
from .common.responses import (
    abort_command,
    cancel_command
)
from .common.api import (
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
    def message_is_valid(self, message: dict) -> bool:
        """
        :param message: Incoming Telegram message.

        :returns: Message is valid and should be handled.
        """
        pass

    @abstractmethod
    def get_attachment(self, message: dict) -> Union[dict, None]:
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
    def create_file_name(self, attachment: dict, file: dict) -> str:
        """
        :param attachment: Not `None` value from `self.get_attachment()`.
        :param file: Representation of this attachment as a file on Telegram
        servers. See https://core.telegram.org/bots/api/#file

        :returns: Name of file which will be uploaded.
        """
        pass

    @yd_access_token_required
    @get_db_data
    def upload(self) -> None:
        """
        Uploads an attachment.
        """
        message = g.incoming_message
        user = g.db_user
        chat = g.db_incoming_chat

        if (not self.message_is_valid(message)):
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

        file = None

        try:
            file = telegram.get_file(
                file_id=attachment["file_id"]
            )
        except Exception as error:
            print(error)
            return cancel_command(chat.telegram_id)

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
                    telegram.send_message(
                        chat_id=chat.telegram_id,
                        text=f"Status: {status}"
                    )
            except YandexAPICreateFolderError as error:
                error_text = str(error) or (
                    "I can't create default upload folder "
                    "due to an unknown Yandex error."
                )

                return telegram.send_message(
                    chat_id=chat.telegram_id,
                    text=error_text
                )
            except YandexAPIUploadFileError as error:
                error_text = str(error) or (
                    "I can't upload this due to an unknown Yandex error."
                )

                return telegram.send_message(
                    chat_id=chat.telegram_id,
                    reply_to_message_id=message["message_id"],
                    text=error_text
                )
            except YandexAPIExceededNumberOfStatusChecksError:
                error_text = (
                    "I can't track operation status of this anymore. "
                    "Perform manual checking."
                )

                return telegram.send_message(
                    chat_id=chat.telegram_id,
                    reply_to_message_id=message["message_id"],
                    text=error_text
                )
            except (YandexAPIRequestError, Exception) as error:
                print(error)
                return cancel_command(chat.telegram_id)

        executor.submit(long_task)


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

    def message_is_valid(self, message):
        return (
            isinstance(
                message.get("photo"),
                list
            ) and
            len(message["photo"]) > 0
        )

    def get_attachment(self, message):
        photos = message["photo"]
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

    def message_is_valid(self, message):
        return (
            isinstance(
                message.get("document"),
                dict
            )
        )

    def get_attachment(self, message):
        return message["document"]

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

    def message_is_valid(self, message):
        return (
            isinstance(
                message.get("audio"),
                dict
            )
        )

    def get_attachment(self, message):
        return message["audio"]

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

    def message_is_valid(self, message):
        return (
            isinstance(
                message.get("video"),
                dict
            )
        )

    def get_attachment(self, message):
        return message["video"]

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

    def message_is_valid(self, message):
        return (
            isinstance(
                message.get("voice"),
                dict
            )
        )

    def get_attachment(self, message):
        return message["voice"]

    def create_file_name(self, attachment, file):
        name = file["file_unique_id"]

        if ("mime_type" in attachment):
            types = attachment["mime_type"].split("/")
            extension = types[1]
            name = f"{name}.{extension}"

        return name


photo_handler = PhotoHandler.handle
file_handler = FileHandler.handle
audio_handler = AudioHandler.handle
video_handler = VideoHandler.handle
voice_handler = VoiceHandler.handle
