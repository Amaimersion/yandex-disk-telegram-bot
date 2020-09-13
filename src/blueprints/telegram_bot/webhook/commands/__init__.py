from .common.names import CommandsNames
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
