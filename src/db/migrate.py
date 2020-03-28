from flask_migrate import Migrate

# we need to import every model in order Migrate know them
from .models import (
    User,
    Chat,
    YandexDiskToken
)


migrate = Migrate()
