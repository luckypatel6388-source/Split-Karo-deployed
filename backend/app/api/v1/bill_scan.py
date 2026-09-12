from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import (
    get_current_user,
)
from app.models.user import User
from app.schemas.bill_scan import (
    BillScanResponse,
)
from app.services.bill_scan_service import (
    BillScanService,
)
from app.core.upload_config import (
    ALLOWED_BILL_TYPES,
    MAX_BILL_FILE_SIZE,
)


router = APIRouter(
    prefix="/bill-scan",
    tags=["Bill Scanner"],
)


@router.post(
    "",
    response_model=BillScanResponse,
)
async def scan_bill(
    file: UploadFile = File(...),
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    if file.content_type not in (
        ALLOWED_BILL_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPEG, PNG and WebP "
                "images are supported."
            ),
        )

    image_bytes = await file.read()

    if len(image_bytes) > MAX_BILL_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Bill image is too large.",
        )

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Empty image.",
        )

    service = BillScanService()

    try:

        result = await service.scan_bill(
            image_bytes=image_bytes,
            content_type=file.content_type,
        )

        if result.confidence < 0.50:
            result.warnings.append(
            "Very low confidence. "
            "Please verify the bill manually."
            )

    except NotImplementedError as exc:

        raise HTTPException(
            status_code=501,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to process the bill."
            ),
        ) from exc

    return BillScanResponse(
        success=True,
        message=(
            "Bill scanned successfully. "
            "Please review the detected "
            "information before confirming."
        ),
        result=result,
    )