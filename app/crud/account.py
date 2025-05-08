from typing import Optional, Sequence, cast

import sqlalchemy
from cachetools import TTLCache, cached
from sqlalchemy.sql import functions as sqlalchemy_functions

from app.model.account import Account
from app.schema.account import AccoundUpdate, AccountDB
from app.util.database_util import get_db
from app.util.exception_util import EntityDoesNotExistError


class AccountCRUD:
    """Class representing the CRUD operations for the Account model."""

    async def create_account(self, account_db: AccountDB) -> Account:
        """Create a new account.

        Args:
            account_db (AccountDB): The account data for creation.

        Returns:
            Account: The created account.
        """
        async for db in get_db():
            new_account = Account(
                id_auth=account_db.id_auth,
                username=account_db.username,
                email=account_db.email,
                is_logged_in=True,
            )

            db.add(instance=new_account)
            await db.commit()
            await db.refresh(instance=new_account)

        return await self.read_account_by_email(email=str(new_account.email))

    @cached(TTLCache(maxsize=1, ttl=100.0))
    async def read_accounts(self) -> Sequence[Account]:
        """Read all accounts.

        Returns:
            Sequence[Account]: A sequence of all accounts.
        """
        async for db in get_db():
            stmt = sqlalchemy.select(Account)
            query = await db.execute(statement=stmt)
        return query.scalars().all()

    async def read_account_by_id(self, id_account: int) -> Account:
        """Read an account by its ID.

        Args:
            id_account (int): The ID of the account.

        Returns:
            Account: The account with the specified ID.

        Raises:
            EntityDoesNotExistError: If the account does not exist.
        """
        async for db in get_db():
            stmt = sqlalchemy.select(Account).where(Account.id_account == id_account)
            query = await db.execute(statement=stmt)

            if not query:
                raise EntityDoesNotExistError(
                    f"Account with id_account `{id_account}` does not exist!",
                )

        result = query.scalar_one_or_none()
        if not result:
            raise EntityDoesNotExistError(
                f"Account with id_account `{id_account}` does not exist!",
            )
        return result

    async def read_account_by_username(self, username: str) -> Account:
        """Read an account by its username.

        Args:
            username (str): The username of the account.

        Returns:
            Account: The account with the specified username.

        Raises:
            EntityDoesNotExistError: If the account does not exist.
        """
        async for db in get_db():
            stmt = sqlalchemy.select(Account).where(Account.username == username)
            query = await db.execute(statement=stmt)

            if not query:
                raise EntityDoesNotExistError(
                    f"Account with username `{username}` does not exist!",
                )

        result = query.scalar_one_or_none()
        if not result:
            raise EntityDoesNotExistError(
                f"Account with username `{username}` does not exist!",
            )
        return result

    async def read_account_by_email(self, email: str) -> Account:
        """Read an account by its email.

        Args:
            email (str): The email of the account.

        Returns:
            Account: The account with the specified email.

        Raises:
            EntityDoesNotExistError: If the account does not exist.
        """
        async for db in get_db():
            stmt = sqlalchemy.select(Account).where(Account.email == email)
            result = await db.execute(statement=stmt)
            account: Optional[Account] = result.scalar_one_or_none()

        if not account:
            raise EntityDoesNotExistError(
                f"Account with email `{email}` does not exist!",
            )
        return account

    async def update_account_by_id(
        self, id_account: int, account_update: AccoundUpdate,
    ) -> Account:
        """Update an account by its ID.

        Args:
            id_account (int): The ID of the account to update.
            account_update (AccountInUpdate): The updated account data.

        Returns:
            Account: The updated account.

        Raises:
            EntityDoesNotExistError: If the account does not exist.
        """
        new_account_data = account_update.dict()

        async for db in get_db():
            select_stmt = sqlalchemy.select(Account).where(Account.id_account == id_account)
            query = await db.execute(statement=select_stmt)
            update_account = query.scalar_one_or_none()

            if not update_account:
                raise EntityDoesNotExistError(
                    f"Account with id_account `{id_account}` does not exist!",
                )

            update_stmt = (
                sqlalchemy.update(table=Account)
                .where(Account.id_account == update_account.id_account)
                .values(updated_at=sqlalchemy_functions.now())
            )

            if new_account_data["username"]:
                update_stmt = update_stmt.values(username=new_account_data["username"])

            await db.execute(statement=update_stmt)
            await db.commit()
            await db.refresh(instance=update_account)

        assert update_account is not None
        return update_account

    async def delete_account_by_id(self, id_account: int) -> str:
        """Delete an account by its ID.

        Args:
            id_account (int): The ID of the account to delete.

        Returns:
            str: A message indicating the success of the deletion.

        Raises:
            EntityDoesNotExistError: If the account does not exist.
        """
        async for db in get_db():
            select_stmt = sqlalchemy.select(Account).where(Account.id_account == id_account)
            query = await db.execute(statement=select_stmt)
            delete_account = query.scalar()

            if not delete_account:
                raise EntityDoesNotExistError(
                    f"Account with id_account `{id_account}` does not exist!",
                )

            stmt = sqlalchemy.delete(table=Account).where(
                Account.id_account == delete_account.id_account,
            )

            await db.execute(statement=stmt)
            await db.commit()

        return f"Account with id_account '{id_account}' is successfully deleted!"

    async def is_admin(self, id_account: int) -> bool:
        """Check if an account is an admin.

        Args:
            id_account (int): The ID of the account.

        Returns:
            bool: True if the account is an admin, False otherwise.
        """
        async for db in get_db():
            stmt = sqlalchemy.select(Account).where(Account.id_account == id_account)
            query = await db.execute(statement=stmt)
            db_account = query.scalar_one_or_none()

        if not db_account:
            raise EntityDoesNotExistError(
                f"Account with id_account `{id_account}` does not exist!",
            )

        return bool(db_account.is_admin)

    async def become_admin(self, id_account: int) -> Account:
        """Make an account an admin.

        Args:
            id_account (int): The ID of the account.

        Returns:
            Account: The account that is now an admin.
        """
        async for db in get_db():
            stmt = (
                sqlalchemy.update(Account)
                .where(Account.id_account == id_account)
                .values(is_admin=True)
            )
            await db.execute(stmt)
            await db.commit()

        return await self.read_account_by_id(id_account=id_account)

    async def remove_admin(self, id_account: int) -> Account:
        """Remove an account as an admin.

        Args:
            id_account (int): The ID of the account.

        Returns:
            Account: The account that is no longer an admin.
        """
        async for db in get_db():
            stmt = (
                sqlalchemy.update(Account)
                .where(Account.id_account == id_account)
                .values(is_admin=False)
            )
            await db.execute(stmt)
            await db.commit()

        return await self.read_account_by_id(id_account=id_account)

    async def get_id_account_from_id_auth(self, id_auth: str) -> int:
        """Get the account ID from the auth ID.

        Args:
            id_auth (str): The ID of the auth.

        Returns:
            int: The ID of the account.
        """
        async for db in get_db():
            stmt = sqlalchemy.select(Account.id_account).where(Account.id_auth == id_auth)
            query = await db.execute(statement=stmt)
        return cast(int, query.scalar())
