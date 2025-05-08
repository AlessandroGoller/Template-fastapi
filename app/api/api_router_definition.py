from fastapi import APIRouter

from app.api.router.v1 import (
    authentication,
    account,
)

router = APIRouter()
router.include_router(authentication.router)
router.include_router(account.router)
