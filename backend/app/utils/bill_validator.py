from decimal import Decimal

from app.schemas.bill_scan import (
    BillScanResult,
)


def validate_bill_result(
    result: BillScanResult,
) -> BillScanResult:

    warnings = list(
        result.warnings
    )

    # -------------------------
    # Confidence validation
    # -------------------------

    if result.confidence < 0.70:

        warnings.append(
            "AI confidence is low. "
            "Please carefully verify the bill."
        )

    # -------------------------
    # Item total validation
    # -------------------------

    calculated_items_total = sum(
        (
            item.total_price
            for item in result.items
        ),
        Decimal("0"),
    )

    if (
        result.total is not None
        and result.items
    ):

        difference = abs(
            calculated_items_total
            - result.total
        )

        if difference > Decimal("0.05"):

            warnings.append(
                "Detected item totals do not "
                "match the final bill total."
            )

    # -------------------------
    # Total validation
    # -------------------------

    if result.total is not None:

        if result.total <= 0:

            warnings.append(
                "Detected bill total is invalid."
            )

    # -------------------------
    # Missing total
    # -------------------------

    if result.total is None:

        warnings.append(
            "Final bill total could not be "
            "reliably detected."
        )

    result.warnings = warnings

    return result