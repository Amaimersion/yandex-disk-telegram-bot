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
    upgrade_users()
    upgrade_chats()


def downgrade():
    downgrade_users()
    downgrade_chats()


def upgrade_users():
    """
    Based on https://stackoverflow.com/a/14845740/8445442
    """
    # Describing of enum
    enum_name = "usergroup"
    temp_enum_name = f"_{enum_name}"
    old_values = ("USER", "TESTER", "ADMIN")
    new_values = ("INVALID", *old_values)
    downgrade_to = ("INVALID", "USER") # on downgrade convert [0] to [1]
    old_type = sa.Enum(*old_values, name=enum_name)
    new_type = sa.Enum(*new_values, name=enum_name)
    temp_type = sa.Enum(*new_values, name=temp_enum_name)

    # Describing of table
    table_name = "users"
    columm_name = "group"
    temp_column = sa.sql.table(
        table_name,
        sa.Column(
            columm_name,
            new_type,
            nullable=False
        )
    )

    temp_type.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            columm_name,
            existing_type=old_type,
            type_=temp_type,
            existing_nullable=False,
            postgresql_using=f'"{columm_name}"::text::{temp_enum_name}'
        )

    old_type.drop(op.get_bind(), checkfirst=False)
    new_type.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            columm_name,
            existing_type=temp_type,
            type_=new_type,
            existing_nullable=False,
            postgresql_using=f'"{columm_name}"::text::{enum_name}'
        )

    temp_type.drop(op.get_bind(), checkfirst=False)


def downgrade_users():
    """
    Based on https://stackoverflow.com/a/14845740/8445442
    """
    # Describing of enum
    enum_name = "usergroup"
    temp_enum_name = f"_{enum_name}"
    old_values = ("USER", "TESTER", "ADMIN")
    new_values = ("INVALID", *old_values)
    downgrade_to = ("INVALID", "USER") # on downgrade convert [0] to [1]
    old_type = sa.Enum(*old_values, name=enum_name)
    new_type = sa.Enum(*new_values, name=enum_name)
    temp_type = sa.Enum(*new_values, name=temp_enum_name)

    # Describing of table
    table_name = "users"
    columm_name = "group"
    temp_column = sa.sql.table(
        table_name,
        sa.Column(
            columm_name,
            new_type,
            nullable=False
        )
    )

    # old enum don't have new value anymore,
    # so we should replace it with somewhat of old values
    op.execute(
        f"UPDATE {table_name} SET \"{columm_name}\" = '{downgrade_to[1]}' "
        f"WHERE \"{columm_name}\" = '{downgrade_to[0]}'"
    )

    temp_type.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            columm_name,
            existing_type=new_type,
            type_=temp_type,
            existing_nullable=False,
            postgresql_using=f'"{columm_name}"::text::{temp_enum_name}'
        )

    new_type.drop(op.get_bind(), checkfirst=False)
    old_type.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            columm_name,
            existing_type=temp_type,
            type_=old_type,
            existing_nullable=False,
            postgresql_using=f'"{columm_name}"::text::{enum_name}'
        )

    temp_type.drop(op.get_bind(), checkfirst=False)


def upgrade_chats():
    """
    Based on https://stackoverflow.com/a/14845740/8445442
    """
    # Describing of enum
    enum_name = "chattype"
    temp_enum_name = f"_{enum_name}"
    old_values = ("PRIVATE", "GROUP", "SUPERGROUP", "CHANNEL")
    new_values = ("UNKNOWN", *old_values)
    downgrade_to = ("UNKNOWN", "PRIVATE") # on downgrade convert [0] to [1]
    old_type = sa.Enum(*old_values, name=enum_name)
    new_type = sa.Enum(*new_values, name=enum_name)
    temp_type = sa.Enum(*new_values, name=temp_enum_name)

    # Describing of table
    table_name = "chats"
    columm_name = "type"
    temp_column = sa.sql.table(
        table_name,
        sa.Column(
            columm_name,
            new_type,
            nullable=False
        )
    )

    temp_type.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            columm_name,
            existing_type=old_type,
            type_=temp_type,
            existing_nullable=False,
            postgresql_using=f'{columm_name}::text::{temp_enum_name}'
        )

    old_type.drop(op.get_bind(), checkfirst=False)
    new_type.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            columm_name,
            existing_type=temp_type,
            type_=new_type,
            existing_nullable=False,
            postgresql_using=f'{columm_name}::text::{enum_name}'
        )

    temp_type.drop(op.get_bind(), checkfirst=False)


def downgrade_chats():
    """
    Based on https://stackoverflow.com/a/14845740/8445442
    """
    # Describing of enum
    enum_name = "chattype"
    temp_enum_name = f"_{enum_name}"
    old_values = ("PRIVATE", "GROUP", "SUPERGROUP", "CHANNEL")
    new_values = ("UNKNOWN", *old_values)
    downgrade_to = ("UNKNOWN", "PRIVATE") # on downgrade convert [0] to [1]
    old_type = sa.Enum(*old_values, name=enum_name)
    new_type = sa.Enum(*new_values, name=enum_name)
    temp_type = sa.Enum(*new_values, name=temp_enum_name)

    # Describing of table
    table_name = "chats"
    columm_name = "type"
    temp_column = sa.sql.table(
        table_name,
        sa.Column(
            columm_name,
            new_type,
            nullable=False
        )
    )

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
            existing_nullable=False,
            postgresql_using=f'{columm_name}::text::{temp_enum_name}'
        )

    new_type.drop(op.get_bind(), checkfirst=False)
    old_type.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            columm_name,
            existing_type=temp_type,
            type_=old_type,
            existing_nullable=False,
            postgresql_using=f'{columm_name}::text::{enum_name}'
        )

    temp_type.drop(op.get_bind(), checkfirst=False)
