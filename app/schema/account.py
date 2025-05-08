from datetime import datetime

from pydantic import EmailStr

from app.schema.base import BaseSchemaModel


class AccoundUpdate(BaseSchemaModel):
    username: str | None = None
    name: str | None = None
    timezone: float | None = None


class AccountBasic(AccoundUpdate):
    email: EmailStr
    is_active: bool | None = None
    is_logged_in: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AccountInCreate(AccountBasic):
    password: str


class AccountDB(AccountBasic):
    id_auth: str


class AccountWithToken(AccountBasic):
    token: str
    refresh_token: str
    expires_in: int


class RefreshToken(BaseSchemaModel):
    token: str
    refresh_token: str
