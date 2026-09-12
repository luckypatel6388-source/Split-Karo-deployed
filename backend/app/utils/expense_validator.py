from decimal import Decimal


def validate_expense_amount(
    amount: Decimal,
):
    if amount <= Decimal("0"):
        raise ValueError(
            "Expense amount must be greater than zero."
        )


def validate_expense_title(
    title: str,
):
    if not title.strip():
        raise ValueError(
            "Expense title cannot be empty."
        )


def validate_item_expense_total(
    expense,
):

    if expense.split_type != "item":
        return

    item_total = sum(
        (
            item.total_price
            for item in expense.items
        ),
        Decimal("0"),
    )

    item_total = item_total.quantize(
        Decimal("0.01")
    )

    expense_amount = Decimal(
        str(expense.amount)
    ).quantize(
        Decimal("0.01")
    )

    if item_total != expense_amount:

        raise ValueError(
            "Item totals must equal "
            "the expense amount."
        )