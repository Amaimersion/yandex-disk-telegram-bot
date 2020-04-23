"""Add BANNED as group type for user model

Revision ID: 67ffbddd6efe
Revises: 375f2ceebbe2
Create Date: 2020-04-23 22:17:46.495174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67ffbddd6efe'
down_revision = '375f2ceebbe2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("group",
            existing_type=sa.Enum("INVALID", "USER", "TESTER", "ADMIN", name="usergroup"),
            type_=sa.Enum("INVALID", "BANNED", "USER", "TESTER", "ADMIN", name="usergroup"),
            existing_nullable=False
        )


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("group",
           existing_type=sa.Enum("INVALID", "BANNED", "USER", "TESTER", "ADMIN", name="usergroup"),
           type_=sa.Enum("INVALID", "USER", "TESTER", "ADMIN", name="usergroup"),
           existing_nullable=False
        )
