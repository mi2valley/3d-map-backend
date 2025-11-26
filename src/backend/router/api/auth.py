from logging import getLogger

from fastapi import APIRouter, Form

from backend.const import TAG_SECURITY
from backend.security import Token, process_get_token

LOG = getLogger(__name__)

router = APIRouter()


@router.post("/token", tags=[TAG_SECURITY], summary="Authorize and get token", response_model_by_alias=True)
async def get_token(
    username: str = Form(None, description=""),  # noqa: B008
    password: str = Form(None, description=""),  # noqa: B008
    grant_type: str = Form(None, description="", regex=r"password"),  # noqa: B008
) -> Token:
    return process_get_token(username, password, grant_type)
