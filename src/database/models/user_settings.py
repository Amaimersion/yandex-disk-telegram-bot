from sqlalchemy.sql import func

from src.extensions import db
from src.i18n import SupportedLanguage


class UserSettings(db.Model):
    """
    Settings of user.

    - it is separate table for convenience, but it must
    exists for every user. So, every time you creating `User`,
    you also should create `UserSettings`.
    """
    __tablename__ = "user_settings"

    # Metadata columns
    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True,
        nullable=False,
        comment="Data related to this user"
    )
    last_update_date = db.Column(
        db.DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Settings columns
    language: SupportedLanguage = db.Column(
        db.Enum(SupportedLanguage),
        default=SupportedLanguage.EN,
        nullable=True,
        comment="Preferred language of user"
    )
    default_upload_folder: str = db.Column(
        db.String,
        nullable=True,
        default="Telegram Bot",
        comment="By default, files will be uploaded in this folder"
    )
    public_upload_by_default: bool = db.Column(
        db.Boolean,
        nullable=True,
        default=False,
        comment=(
            "Until user explicitly specifies, public uploading "
            "will be used by default instead of private one"
        )
    )

    # Relationships
    user = db.relationship(
        "User",
        back_populates="settings",
        uselist=False
    )

    def __repr__(self):
        return f"<User {self.user_id} settings>"

    @staticmethod
    def create_fake(user):
        """
        Creates fake user settings.

        :param user:
        User to associate created settings with.
        """
        from faker import Faker

        fake = Faker()
        result = UserSettings(user=user)

        result.last_update_date = fake.date_time_between_dates(
            datetime_start=user.create_date,
            tzinfo=None
        )
        result.language = fake.random_element(list(SupportedLanguage))
        result.default_upload_folder = fake.file_path()
        result.public_upload_by_default = fake.random_element([True, False])

        return result
