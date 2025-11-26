from logging import getLogger

from fastapi import APIRouter, Security

from backend.const import TAG_USER
from backend.model.user import User
from backend.security import TokenModel, get_token_oauth2_password_bearer

LOG = getLogger(__name__)
router = APIRouter()


@router.get("/users/me", tags=[TAG_USER])
async def api_get_users_me(user: TokenModel = Security(get_token_oauth2_password_bearer, scopes=[])) -> User:
    return User(id=user.sub)
