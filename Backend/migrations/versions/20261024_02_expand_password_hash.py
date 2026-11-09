"""Expand password hash storage to 255 characters.

Revision ID: 20261024_02
Revises: 20261024_01
Create Date: 2026-10-24
"""
from alembic import op
import sqlalchemy as sa

revision = "20261024_02"
down_revision = "20261024_01"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=sa.String(length=120),
            type_=sa.String(length=255),
            existing_nullable=True,
        )


def downgrade():
    bind = op.get_bind()
    has_long_hash = bind.execute(
        sa.text(
            "SELECT 1 FROM user "
            "WHERE password_hash IS NOT NULL "
            "AND length(password_hash) > 120 LIMIT 1"
        )
    ).first()

    if has_long_hash:
        raise RuntimeError(
            "Cannot shrink password_hash to 120 characters: "
            "one or more stored hashes are longer than 120 characters."
        )

    with op.batch_alter_table("user") as batch_op:
        batch_op.alter_column(
            "password_hash",
            existing_type=sa.String(length=255),
            type_=sa.String(length=120),
            existing_nullable=True,
        )
