from decimal import Decimal


def optimize_settlements(
    balances: dict[str, Decimal],
):
    creditors = []
    debtors = []

    for user_id, balance in balances.items():

        if balance > Decimal("0"):
            creditors.append(
                [
                    user_id,
                    balance,
                ]
            )

        elif balance < Decimal("0"):
            debtors.append(
                [
                    user_id,
                    -balance,
                ]
            )

    settlements = []

    creditor_index = 0
    debtor_index = 0

    while (
        creditor_index < len(creditors)
        and debtor_index < len(debtors)
    ):

        creditor_id = creditors[
            creditor_index
        ][0]

        creditor_amount = creditors[
            creditor_index
        ][1]

        debtor_id = debtors[
            debtor_index
        ][0]

        debtor_amount = debtors[
            debtor_index
        ][1]

        transfer = min(
            creditor_amount,
            debtor_amount,
        )

        if transfer > Decimal("0"):

            settlements.append(
                {
                    "from_user_id": debtor_id,
                    "to_user_id": creditor_id,
                    "amount": transfer,
                }
            )

        creditors[creditor_index][1] -= transfer
        debtors[debtor_index][1] -= transfer

        if (
            creditors[creditor_index][1]
            <= Decimal("0.00")
        ):
            creditor_index += 1

        if (
            debtors[debtor_index][1]
            <= Decimal("0.00")
        ):
            debtor_index += 1

    return settlements