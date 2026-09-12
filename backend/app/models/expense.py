import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Expense(TimestampMixin, Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    group_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey(
            "groups.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    paid_by: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    split_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    expense_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    participants = relationship(
        "ExpenseParticipant",
        back_populates="expense",
        cascade="all, delete-orphan",
    )

    items = relationship(
    "ExpenseItem",
    back_populates="expense",
    cascade="all, delete-orphan",
    )

    group = relationship(
        "Group",
    )

    payer = relationship(
        "User",
        foreign_keys=[paid_by],
    )