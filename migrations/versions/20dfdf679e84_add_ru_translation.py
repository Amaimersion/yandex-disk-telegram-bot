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

# Describing of enum
enum_name = "supportedlanguage"
temp_enum_name = f"_{enum_name}"
old_values = ("EN",)
new_values = ("RU", *old_values)
downgrade_to = ("RU", "EN") # on downgrade convert [0] to [1]
old_type = sa.Enum(*old_values, name=enum_name)
new_type = sa.Enum(*new_values, name=enum_name)
temp_type = sa.Enum(*new_values, name=temp_enum_name)

# Describing of table
table_name = "user_settings"
columm_name = "language"


def upgrade():
    """
    Based on https://stackoverflow.com/a/14845740/8445442
    """
    temp_type.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            columm_name,
            existing_type=old_type,
            type_=temp_type,
            existing_nullable=True,
            postgresql_using=f'{columm_name}::text::{temp_enum_name}'
        )

    old_type.drop(op.get_bind(), checkfirst=False)
    new_type.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            columm_name,
            existing_type=temp_type,
            type_=new_type,
            existing_nullable=True,
            postgresql_using=f'{columm_name}::text::{enum_name}'
        )

    temp_type.drop(op.get_bind(), checkfirst=False)


def downgrade():
    """
    Based on https://stackoverflow.com/a/14845740/8445442
    """
    # old enum don't have new value anymore,
    # so we should replace it with somewhat of old values
    op.execute(
        f"UPDATE {table_name} SET {columm_name} = '{downgrade_to[1]}' "
        f"WHERE {columm_name} = '{downgrade_to[0]}'"
    )

    temp_type.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            columm_name,
            existing_type=new_type,
            type_=temp_type,
            existing_nullable=True,
            postgresql_using=f'{columm_name}::text::{temp_enum_name}'
        )

    new_type.drop(op.get_bind(), checkfirst=False)
    old_type.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            columm_name,
            existing_type=temp_type,
            type_=old_type,
            existing_nullable=True,
            postgresql_using=f'{columm_name}::text::{enum_name}'
        )

    temp_type.drop(op.get_bind(), checkfirst=False)
