from decimal import Decimal


def validate_settlement_users(
    from_user_id: str,
    to_user_id: str,
):
    if from_user_id == to_user_id:
        raise ValueError(
            "A user cannot settle with themselves."
        )


def validate_settlement_amount(
    amount: Decimal,
):
    if amount <= Decimal("0"):
        raise ValueError(
            "Settlement amount must be greater than zero."
        )


def validate_settlement_against_balance(
    amount: Decimal,
    actual_owed: Decimal,
):
    amount = Decimal(str(amount)).quantize(
        Decimal("0.01")
    )

    actual_owed = Decimal(
        str(actual_owed)
    ).quantize(
        Decimal("0.01")
    )

    if amount > actual_owed:
        raise ValueError(
            f"Settlement amount cannot exceed "
            f"the user's current owed amount "
            f"of ₹{actual_owed}."
        )