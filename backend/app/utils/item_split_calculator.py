from decimal import Decimal


CENT = Decimal("0.01")


def calculate_item_total(
    quantity: Decimal,
    unit_price: Decimal,
) -> Decimal:

    return (
        quantity * unit_price
    ).quantize(CENT)


def validate_item_shares(
    total_price: Decimal,
    shares: dict[str, Decimal],
) -> None:

    if not shares:
        raise ValueError(
            "At least one participant is required."
        )

    for user_id, share in shares.items():

        if share <= 0:
            raise ValueError(
                f"Share must be greater than zero: "
                f"{user_id}"
            )

        if share.as_tuple().exponent < -2:#type:ignore
            raise ValueError(
                "Share cannot have more than "
                "2 decimal places."
            )

    total_shares = sum(
        shares.values(),
        Decimal("0"),
    )

    total_shares = total_shares.quantize(
        CENT
    )

    if total_shares != total_price:

        raise ValueError(
            f"Item shares must equal item price. "
            f"Expected {total_price}, "
            f"got {total_shares}."
        )