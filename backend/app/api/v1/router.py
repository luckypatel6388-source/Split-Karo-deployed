from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.groups import router as groups_router
from app.api.v1.invites import router as invites_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.balances import router as balances_router
from app.api.v1.settlements import router as settlements_router
from app.api.v1.expense_items import (
    router as expense_items_router,
)
from app.api.v1.expense_detail import (
    router as expense_detail_router,
)
from app.api.v1.expense_management import (
    router as expense_management_router,
)
from app.api.v1.settlement_management import (
    router as settlement_management_router,
)

from app.api.v1.bill_scan import (
    router as bill_scan_router,
)
from app.api.v1.payments import router as payments_router
from app.api.v1.users import router as users_router

api_router = APIRouter()


@api_router.get(
    "/health",
    tags=["System"],
)
async def api_health_check():
    return {
        "status": "ok",
        "api_version": "v1",
    }


api_router.include_router(auth_router)
api_router.include_router(groups_router)
api_router.include_router(invites_router)
api_router.include_router(expenses_router)
api_router.include_router(balances_router)
api_router.include_router(settlements_router)
api_router.include_router(expense_items_router)
api_router.include_router(expense_detail_router)
api_router.include_router(expense_management_router)
api_router.include_router(settlement_management_router)
api_router.include_router(bill_scan_router)
api_router.include_router(payments_router)
api_router.include_router(users_router)