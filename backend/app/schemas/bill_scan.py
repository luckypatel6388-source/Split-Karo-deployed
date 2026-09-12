from decimal import Decimal

from pydantic import BaseModel, Field


class ExtractedBillItem(BaseModel):
    name: str
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    total_price: Decimal = Field(ge=0)


class BillScanResult(BaseModel):
    merchant_name: str | None = None
    bill_date: str | None = None

    subtotal: Decimal | None = None
    tax: Decimal | None = None
    discount: Decimal | None = None
    total: Decimal | None = None

    items: list[ExtractedBillItem] = []

    confidence: float = Field(
        ge=0,
        le=1,
    )

    warnings: list[str] = []

    raw_text: str | None = None


class BillScanResponse(BaseModel):
    success: bool
    message: str
    result: BillScanResult

