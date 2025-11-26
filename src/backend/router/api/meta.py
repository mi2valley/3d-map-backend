from logging import getLogger

from fastapi import APIRouter

from backend.const import TAG_METADATA, VERSION
from backend.model.metadata import Health, Version

LOG = getLogger(__name__)
router = APIRouter()


@router.get("/health", tags=[TAG_METADATA])
async def health() -> Health:
    return Health(status="ok")


@router.get("/version", tags=[TAG_METADATA])
async def version() -> Version:
    return Version(version=VERSION)
