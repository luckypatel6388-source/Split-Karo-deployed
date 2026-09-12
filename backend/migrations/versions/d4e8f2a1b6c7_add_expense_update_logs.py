"""add expense update logs

Revision ID: d4e8f2a1b6c7
Revises: 8c1f994df6e2
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "d4e8f2a1b6c7"
down_revision: Union[str, Sequence[str], None] = "8c1f994df6e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "expense_update_logs",
        sa.Column("id", mysql.CHAR(36), nullable=False),
        sa.Column("expense_id", mysql.CHAR(36), nullable=False),
        sa.Column("updated_by", mysql.CHAR(36), nullable=False),
        sa.Column("previous_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("updated_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("previous_title", sa.String(150), nullable=True),
        sa.Column("updated_title", sa.String(150), nullable=True),
        sa.Column("previous_description", sa.Text(), nullable=True),
        sa.Column("updated_description", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["expense_id"], ["expenses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_expense_update_logs_expense_id", "expense_update_logs", ["expense_id"])
    op.create_index("ix_expense_update_logs_updated_by", "expense_update_logs", ["updated_by"])


def downgrade() -> None:
    op.drop_index("ix_expense_update_logs_updated_by", table_name="expense_update_logs")
    op.drop_index("ix_expense_update_logs_expense_id", table_name="expense_update_logs")
    op.drop_table("expense_update_logs")
