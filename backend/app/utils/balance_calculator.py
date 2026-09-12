from decimal import Decimal

from app.models.settlement import Settlement
from app.services.expense_calculation_service import (
    calculate_expense_user_shares,
)


def calculate_balances(
    expenses,
    settlements=None,
) -> dict[str, Decimal]:

    balances: dict[str, Decimal] = {}

    for expense in expenses:

        payer_id = expense.paid_by

        balances.setdefault(
            payer_id,
            Decimal("0"),
        )

        balances[payer_id] += Decimal(
            str(expense.amount)
        )

        user_shares = (
            calculate_expense_user_shares(
                expense
            )
        )

        for user_id, share in user_shares.items():

            balances.setdefault(
                user_id,
                Decimal("0"),
            )

            balances[user_id] -= Decimal(
                str(share)
            )

    # Apply completed settlements.
    if settlements:

        for settlement in settlements:

            if settlement.status != "paid":
                continue

            from_user = (
                settlement.from_user_id
            )

            to_user = (
                settlement.to_user_id
            )

            amount = Decimal(
                str(settlement.amount)
            )

            balances.setdefault(
                from_user,
                Decimal("0"),
            )

            balances.setdefault(
                to_user,
                Decimal("0"),
            )

            # Person who paid gets their debt reduced.
            balances[from_user] += amount

            # Person receiving payment gets
            # their credit reduced.
            balances[to_user] -= amount

    return balances