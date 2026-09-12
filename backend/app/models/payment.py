import uuid
from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class PaymentAttempt(TimestampMixin, Base):
    __tablename__ = "payment_attempts"

    __table_args__ = (
        UniqueConstraint(
            "payer_user_id",
            "idempotency_key",
            name="uq_payment_payer_idempotency",
        ),
    )

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

    settlement_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey(
            "settlements.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    payer_user_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    receiver_user_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="created",
        index=True,
    )

    payment_method: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="upi",
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    payment_reference: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    upi_uri: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    group = relationship(
        "Group",
    )

    settlement = relationship(
        "Settlement",
    )

    payer = relationship(
        "User",
        foreign_keys=[payer_user_id],
    )

    receiver = relationship(
        "User",
        foreign_keys=[receiver_user_id],
    )