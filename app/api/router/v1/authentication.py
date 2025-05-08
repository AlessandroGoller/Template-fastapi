from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.core.securities.auth import create_new_account, sign_in_account, update_token
from app.schema.account import (
    AccountBasic,
    AccountInCreate,
    AccountWithToken,
    RefreshToken,
)
from app.schema.auth import AuthSchema

router = APIRouter(prefix="/v1/auth", tags=["authentication"])


@router.post(
    "/signup",
    name="auth:signup",
    response_model=AccountWithToken,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    account_create: AccountInCreate,
) -> AccountWithToken:
    """
    Create a new account.

    Args:
        account_create (AccountInCreate): The account details for creating a new account.

    Returns:
        AccountWithToken: The newly created account.

    """
    try:
        new_account: AccountBasic = create_new_account(account_create)
        return sign_in_account(
            AuthSchema(email=new_account.email, password=account_create.password),
        )
    except Exception as exc:
        logger.error(f"Account creation failed due to {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account creation failed",
        ) from None


@router.post(
    path="/signin",
    name="auth:signin",
    response_model=AccountWithToken,
    status_code=status.HTTP_202_ACCEPTED,
)
def signin(
    account_login: AuthSchema,
) -> AccountWithToken:
    """
    Sign in to the application using the provided account login credentials.

    Args:
        account_login (AuthSchema): The account login credentials.

    Returns:
        AccountWithToken: The account information along with an authentication token.
    """
    return sign_in_account(account_login)


@router.post(
    path="/refresh",
    name="auth:refresh",
    response_model=RefreshToken,
    status_code=status.HTTP_200_OK,
)
def refresh(
    token: str,
) -> RefreshToken:
    """
    Refresh the given token.

    Args:
        token (str): The token to be refreshed.

    Returns:
        str: The new token.
    """
    return update_token(token)
