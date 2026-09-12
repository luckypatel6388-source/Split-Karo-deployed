from decimal import Decimal
from urllib.parse import urlencode


def create_upi_uri(
    *,
    payee_vpa: str,
    payee_name: str,
    amount: Decimal,
    transaction_reference: str,
    note: str,
) -> str:
    """
    Create a standard UPI deep-link URI.

    This URI does not complete a payment by itself.
    It opens a compatible UPI application where the
    user must authorize the payment.
    """

    payee_vpa = payee_vpa.strip()
    payee_name = payee_name.strip()

    if not payee_vpa:
        raise ValueError(
            "Receiver UPI ID is required."
        )

    if not payee_name:
        raise ValueError(
            "Receiver name is required."
        )

    amount = Decimal(
        str(amount)
    ).quantize(
        Decimal("0.01")
    )

    if amount <= Decimal("0.00"):
        raise ValueError(
            "UPI payment amount must be greater than zero."
        )

    transaction_reference = (
        transaction_reference.strip()
    )

    if not transaction_reference:
        raise ValueError(
            "Payment reference is required."
        )

    params = {
        "pa": payee_vpa,
        "pn": payee_name,
        "am": f"{amount:.2f}",
        "cu": "INR",
        "tr": transaction_reference,
        "tn": note.strip(),
    }

    return (
        "upi://pay?"
        + urlencode(params)
    )














"""from decimal import Decimal
from urllib.parse import urlencode


def create_upi_uri(
    *,
    payee_vpa: str,
    payee_name: str,
    amount: Decimal,
    transaction_reference: str,
    note: str,
) -> str:

    amount_value = (
        Decimal(str(amount))
        .quantize(Decimal("0.01"))
    )

    if amount_value <= Decimal("0.00"):
        raise ValueError(
            "UPI amount must be greater than zero."
        )

    if not payee_vpa:
        raise ValueError(
            "Receiver UPI ID is not configured."
        )

    params = urlencode(
        {
            "pa": payee_vpa,
            "pn": payee_name,
            "am": f"{amount_value:.2f}",
            "cu": "INR",
            "tr": transaction_reference,
            "tn": note,
        }
    )

    return f"upi://pay?{params}"""