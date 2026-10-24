"""Create the current user table baseline.

Revision ID: 20261024_01
Revises:
Create Date: 2026-10-24
"""
from alembic import op
import sqlalchemy as sa

revision = "20261024_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=120), nullable=True),
        sa.Column("role", sa.String(length=64), nullable=True),
        sa.Column("reset_token", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("reset_token"),
    )
    op.create_index("ix_user_username", "user", ["username"], unique=False)
    op.create_index("ix_user_email", "user", ["email"], unique=False)


def downgrade():
    op.drop_index("ix_user_email", table_name="user")
    op.drop_index("ix_user_username", table_name="user")
    op.drop_table("user")
