from fastapi import APIRouter, Query, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from freelance_marketplace.api.services.authentication import Authentication
from freelance_marketplace.api.services.redis import Redis
from freelance_marketplace.db.sql.database import get_sql_db
from freelance_marketplace.models.requests.loginRequest import LoginRequest

router = APIRouter()

@router.post("/login", tags=["auth"])
async def login(
    login_request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_sql_db)
):
    await Authentication.verify_nonce(login_request=login_request)
    await Authentication.verify_signature(login_request=login_request)
    await Authentication.user_conditional_register(login_request=login_request, db=db)
    access_token = await Authentication.create_access_token(login_request=login_request, response=response)
    return access_token


@router.post("/logout", tags=["auth"])
async def logout(
        response: Response,
        request: Request
):
    await Authentication.logout(response=response, request=request)
    return True

@router.get("/nonce", tags=["auth"])
async def retrieve_nonce(
        wallet_address: str = Query(...)
):
    nonce = await Authentication.generate_nonce(length=32)
    await Redis.set_redis_data(cache_key=f"nonce:{wallet_address}", data=nonce)
    return nonce