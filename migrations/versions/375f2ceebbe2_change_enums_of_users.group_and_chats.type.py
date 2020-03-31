"""Change enums of users.group and chats.type

Revision ID: 375f2ceebbe2
Revises: 358b1cefda13
Create Date: 2020-03-31 21:40:42.267390

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "375f2ceebbe2"
down_revision = "358b1cefda13"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("group",
               existing_type=sa.Enum("USER", "TESTER", "ADMIN", name="usergroup"),
               type_=sa.Enum("INVALID", "USER", "TESTER", "ADMIN", name="usergroup"),
               existing_nullable=False)

    with op.batch_alter_table("chats") as batch_op:
        batch_op.alter_column("type",
               existing_type=sa.Enum("PRIVATE", "GROUP", "SUPERGROUP", "CHANNEL", name="chattype"),
               type_=sa.Enum("UNKNOWN", "PRIVATE", "GROUP", "SUPERGROUP", "CHANNEL", name="chattype"),
               existing_nullable=False)


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("group",
               existing_type=sa.Enum("INVALID", "USER", "TESTER", "ADMIN", name="usergroup"),
               type_=sa.Enum("USER", "TESTER", "ADMIN", name="usergroup"),
               existing_nullable=False)

    with op.batch_alter_table("chats") as batch_op:
        batch_op.alter_column("type",
               existing_type=sa.Enum("UNKNOWN", "PRIVATE", "GROUP", "SUPERGROUP", "CHANNEL", name="chattype"),
               type_=sa.Enum("PRIVATE", "GROUP", "SUPERGROUP", "CHANNEL", name="chattype"),
               existing_nullable=False)
