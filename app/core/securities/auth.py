import pyrebase
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from loguru import logger

from app.config import settings
from app.crud.account import AccountCRUD
from app.schema.account import (
    AccountBasic,
    AccountDB,
    AccountInCreate,
    AccountWithToken,
    RefreshToken,
)
from app.schema.auth import AuthSchema

firebase = pyrebase.initialize_app(settings.firebase_config)
auth = firebase.auth()


def create_new_account(account_create: AccountInCreate) -> AccountBasic:
    """
    Creates a new user account.

    Args:
        account_create (AccountInCreate): The account details for creating a new account.

    Returns:
        AccountBasic: The basic account information of the newly created account.

    Raises:
        HTTPException: If an account with the same email already exists.

    """
    try:
        user = auth.create_user_with_email_and_password(
            email=account_create.email, password=account_create.password,
        )
        auth.send_email_verification(user["idToken"])

    except Exception as exc:
        logger.error(
            f"Account creation failed due to {exc}, email {account_create.email}",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account creation failed",
        ) from None

    account_db = AccountDB(
        id_auth=user["localId"],
        email=account_create.email,
        is_logged_in=True,
        is_active=True,
    )
    new_account = AccountCRUD().create_account(account_db=account_db)

    # TODO: se c'è un errore rimuoverlo anche da firebase
    return AccountBasic.from_orm(new_account)


def sign_in_account(auth_schema: AuthSchema) -> AccountWithToken:
    """
    Signs in an account using the provided authentication schema.

    Args:
        auth_schema (AuthSchema): The authentication schema containing the email and password.

    Returns:
        AccountWithToken: An object containing the account token and other account details.

    Raises:
        HTTPException: If the login fails due to invalid credentials.
    """
    email = auth_schema.email
    password = auth_schema.password

    try:
        user = auth.sign_in_with_email_and_password(email=email, password=password)
        token = user["idToken"]
        refresh_token = user["refreshToken"]
        expires_in = user["expiresIn"]

    except Exception as exc:
        logger.error(f"Login failed due to {exc}, account with email {email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Credentials",
        ) from None

    account = AccountCRUD().read_account_by_email(email=email)
    return AccountWithToken.from_orm(account).model_copy(update={
        "token": token,
        "refresh_token": refresh_token,
        "expires_in": expires_in,
    })


async def get_id_account_from_token(
    token: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> int:
    """
    Retrieves the account ID associated with the given token.

    Args:
        token (HTTPAuthorizationCredentials): The token to verify.

    Returns:
        int: The account ID associated with the token.

    Raises:
        HTTPException: If the token verification fails.
    """
    try:
        info = auth.get_account_info(token.credentials)
        user = info["users"][0]
        return await AccountCRUD().get_id_account_from_id_auth(user["localId"])
    except Exception as exc:
        logger.error(f"Token verification failed due to {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Token",
        ) from None


async def delete_account_by_id_account(id_account: int, token: str) -> str:
    """
    Deletes an account by its ID.

    Args:
        id_account (int): The ID of the account to be deleted.

    Returns:
        str: A message indicating the success of the deletion.

    Raises:
        HTTPException: If the account deletion fails.

    """
    try:
        auth.delete_user_account(token)
        return await AccountCRUD().delete_account_by_id(id_account=id_account)
    except Exception as exc:
        logger.error(f"Account deletion failed due to {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account deletion failed",
        ) from None


def update_token(token: str) -> RefreshToken:
    """
    Refreshes the given token and returns the new token.

    Args:
        token: The token to be refreshed.

    Returns:
        str: The new token.

    Raises:
        HTTPException: If the token refresh fails.
    """
    try:
        new_token = auth.refresh(token)
        return RefreshToken(
            token=new_token["idToken"],
            refresh_token=new_token["refreshToken"],
        )
    except Exception as exc:
        logger.error(f"Token refresh failed due to {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token refresh failed",
        ) from None
