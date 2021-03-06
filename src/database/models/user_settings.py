from sqlalchemy.sql import func

from src.extensions import db


class UserSettings(db.Model):
    """
    Settings of user.

    - it is separate table for convenience, but it must
    exists for every user. So, every time you creating `User`,
    you also should create `UserSettings`.
    """
    __tablename__ = "user_settings"

    # Metadata columns
    user_id = db.Column(
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
    default_upload_folder = db.Column(
        db.String,
        nullable=True,
        default="Telegram Bot",
        comment="By default, files will be uploaded in this folder"
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
        result.default_upload_folder = fake.file_path()

        return result
