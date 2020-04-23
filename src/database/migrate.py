from flask_migrate import Migrate

# we need to import every model in order Migrate knows them
from .models import * # noqa


migrate = Migrate(
    compare_type=True,
    render_as_batch=True
)
