from decimal import Decimal


def calculate_expense_user_shares(
    expense,
) -> dict[str, Decimal]:
    """
    Returns the final amount owed by each user
    for an expense.
    """

    shares: dict[str, Decimal] = {}

    # Normal equal/custom expense
    if expense.split_type in {
        "equal",
        "custom",
    }:
        for participant in expense.participants:
            shares[participant.user_id] = (
                shares.get(
                    participant.user_id,
                    Decimal("0"),
                )
                + participant.share_amount
            )

        return shares

    # Item-based expense
    if expense.split_type == "item":

        for item in expense.items:
            for participant in item.participants:

                shares[
                    participant.user_id
                ] = (
                    shares.get(
                        participant.user_id,
                        Decimal("0"),
                    )
                    + participant.share_amount
                )

        return shares

    raise ValueError(
        f"Unsupported split type: "
        f"{expense.split_type}"
    )