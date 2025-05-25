from fastapi import APIRouter

from .divingfish import router as divingfish_router
from .dxrating import router as dxrating_router


router = APIRouter(
    prefix="/v1",
    tags=["v1"]
)

router.include_router(divingfish_router)
router.include_router(dxrating_router)

