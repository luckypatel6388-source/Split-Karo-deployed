from decimal import Decimal, ROUND_DOWN


CENT = Decimal("0.01")


def calculate_equal_split(
    amount: Decimal,
    participant_ids: list[str],
) -> dict[str, Decimal]:

    if not participant_ids:
        raise ValueError(
            "At least one participant is required."
        )

    if amount <= 0:
        raise ValueError(
            "Amount must be greater than zero."
        )

    participant_count = len(participant_ids)

    base_share = (
        amount / participant_count
    ).quantize(
        CENT,
        rounding=ROUND_DOWN,
    )

    shares = {
        user_id: base_share
        for user_id in participant_ids
    }

    distributed = (
        base_share * participant_count
    )

    remainder = amount - distributed

    # Distribute leftover cents deterministically.
    index = 0

    while remainder > Decimal("0"):
        user_id = participant_ids[index]

        shares[user_id] += CENT

        remainder -= CENT

        index += 1

        if index >= participant_count:
            index = 0

    return shares


def validate_custom_split(
    amount: Decimal,
    shares: dict[str, Decimal],
) -> None:

    if not shares:
        raise ValueError(
            "Custom split requires at least one participant."
        )

    for user_id, share in shares.items():

        if share < 0:
            raise ValueError(
                f"Share cannot be negative: {user_id}"
            )

        if share.as_tuple().exponent < -2: #type:ignore
            raise ValueError(
                "Shares cannot have more than 2 decimal places."
            )

    total = sum(
        shares.values(),
        Decimal("0"),
    )

    if total != amount:
        raise ValueError(
            f"Custom shares must equal the expense amount. "
            f"Expected {amount}, got {total}."
        )