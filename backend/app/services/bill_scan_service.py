from app.schemas.bill_scan import (
    BillScanResult,
    ExtractedBillItem,
)

from app.services.bill_ai_service import (
    BillAIService,
)

from app.utils.bill_validator import (
    validate_bill_result,
)


class BillScanService:

    def __init__(self):

        self.ai_service = (
            BillAIService()
        )

    async def scan_bill(
        self,
        image_bytes: bytes,
        content_type: str,
    ) -> BillScanResult:

        extracted = (
            await self.ai_service.extract_bill(
                image_bytes=image_bytes,
                content_type=content_type,
            )
        )

        result = BillScanResult(
            merchant_name=(
                extracted.get(
                    "merchant_name"
                )
            ),
            bill_date=(
                extracted.get(
                    "bill_date"
                )
            ),
            subtotal=(
                extracted.get(
                    "subtotal"
                )
            ),
            tax=(
                extracted.get(
                    "tax"
                )
            ),
            discount=(
                extracted.get(
                    "discount"
                )
            ),
            total=(
                extracted.get(
                    "total"
                )
            ),
            items=[
                ExtractedBillItem(**item)
                for item in extracted.get(
                    "items",
                    [],
                )
            ],
            confidence=extracted.get(
                "confidence",
                0,
            ),
            warnings=extracted.get(
                "warnings",
                [],
            ),
        )

        return validate_bill_result(
            result
        )