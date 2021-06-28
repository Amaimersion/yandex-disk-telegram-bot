"""Add RU translation

Revision ID: 20dfdf679e84
Revises: 5b1c342f1989
Create Date: 2021-06-26 21:00:22.058352

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20dfdf679e84'
down_revision = '5b1c342f1989'
branch_labels = None
depends_on = None

enum_name = "supportedlanguage"
old_values = ("EN",)
new_values = old_values + ("RU",)


def upgrade():
    with op.batch_alter_table("user_settings") as batch_op:
        batch_op.alter_column("language",
            existing_type=sa.Enum(*old_values, name=enum_name),
            type_=sa.Enum(*new_values, name=enum_name),
            existing_nullable=True
        )


def downgrade():
    with op.batch_alter_table("user_settings") as batch_op:
        batch_op.alter_column("language",
            existing_type=sa.Enum(*new_values, name=enum_name),
            type_=sa.Enum(*old_values, name=enum_name),
            existing_nullable=True
        )
