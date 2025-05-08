from fastapi import APIRouter, Depends, HTTPException, status

from app.core.securities.auth import get_id_account_from_token
from app.crud.account import AccountCRUD
from app.schema.account import AccountBasic
from app.util.exception_util import EntityDoesNotExistError

router = APIRouter(prefix="/v1/accounts", tags=["accounts"])


@router.get(
    path="",
    name="accounts:read-accounts",
    response_model=list[AccountBasic],
    status_code=status.HTTP_200_OK,
)
async def get_accounts(
    id_account: int = Depends(get_id_account_from_token),
) -> list[AccountBasic]:
    """
    Retrieve a list of accounts.

    Returns:
        list[AccountBasic]: A list of accounts with their details.
    """
    if not await AccountCRUD().is_admin(id_account=id_account):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view the accounts!",
        )
    db_accounts = await AccountCRUD().read_accounts()
    db_account_list: list = []

    for db_account in db_accounts:
        account = AccountBasic.from_orm(db_account)
        db_account_list.append(account)

    return db_account_list


@router.get(
    path="/{id_account}",
    name="accounts:read-account-by-id_account",
    response_model=AccountBasic,
    status_code=status.HTTP_200_OK,
)
async def get_account(
    id_account: int, id_account_current: int = Depends(get_id_account_from_token),
) -> AccountBasic:
    """
    Retrieve account information by id_account.

    Args:
        id_account (int): The ID of the account to retrieve.
        id_account_current (int, optional): The ID of the current account. Defaults to the ID obtained from the token.

    Returns:
        AccountBasic: The account information.

    Raises:
        HTTPException: If the current account is not authorized to view the account or if the account does not exist.
    """
    if id_account_current != id_account and not await AccountCRUD().is_admin(
        id_account=id_account_current,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view the account!",
        )

    try:
        db_account = await AccountCRUD().read_account_by_id(id_account=id_account)

    except EntityDoesNotExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with id_account `{id_account}` does not exist!",
        ) from None

    return AccountBasic.from_orm(db_account)

# TODO: update account, change password / ...
