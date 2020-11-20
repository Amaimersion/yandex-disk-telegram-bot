"""
How to create handler for the dispatcher:
- you should provide one function. This function
will be called to handle an incoming Telegram message
- dispatcher handles any handler exceptions, so, if
any unexpected error occurs you can raise the exception.
Sure, you can raise your own exception for nice debug
- edit dispatcher module in order to register your handler
- handler should accept only `(*args, **kwargs)` arguments
- dispatcher passes in `**kwargs`: `route_source: RouteSource`,
`message_events: Set[str]` (`str` it is `DispatcherEvent` values),
`user_id: int`, `chat_id: int`, `message: TelegramMessage`.
These values can have `None` value, so, check for it before using.
For another values in `*args` and `**kwargs` see documentation of
functions from call stack of dispatcher function.

How to create stateful chat:
- use `set_disposable_handler`, `subscribe_handler`,
`unsubcribe_handler`, `set/get/delete_user/user_chat/chat_data`
- if you want to provide Enum, then provide value of that enum,
not object directly
"""


from .unknown import handle as unknown_handler
from .help import handle as help_handler
from .about import handle as about_handler
from .settings import handle as settings_handler
from .yd_auth import handle as yd_auth_handler
from .yd_revoke import handle as yd_revoke_handler
from .upload import handle_photo as upload_photo_handler
from .upload import handle_file as upload_file_handler
from .upload import handle_audio as upload_audio_handler
from .upload import handle_video as upload_video_handler
from .upload import handle_voice as upload_voice_handler
from .upload import handle_url as upload_url_handler
from .create_folder import handle as create_folder_handler
from .publish import handle as publish_handler
from .unpublish import handle as unpublish_handler
from .space import handle as space_handler
from .element_info import handle as element_info_handler
