import uuid
from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ExpenseItemParticipant(
    TimestampMixin,
    Base,
):
    __tablename__ = "expense_item_participants"

    id: Mapped[str] = mapped_column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    item_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey(
            "expense_items.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    share_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    item = relationship(
        "ExpenseItem",
        back_populates="participants",
    )

    user = relationship(
        "User",
    )

    __table_args__ = (
        UniqueConstraint(
            "item_id",
            "user_id",
            name="uq_expense_item_participant",
        ),
    )