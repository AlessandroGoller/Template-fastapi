from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, schema
from sqlalchemy.sql import functions as sqlalchemy_functions

from app.util.database_util import database


class Account(database):
    __tablename__ = "account"

    id_account = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    id_auth = Column(String(length=64), nullable=False, unique=True)
    username = Column(String(length=64), nullable=True, unique=True)
    email = Column(String(length=64), nullable=False, unique=True)
    name = Column(String(length=64), nullable=True)
    is_active = Column(Boolean, default=False)
    is_logged_in = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy_functions.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_onupdate=schema.FetchedValue(for_update=True),
    )
    timezone = Column(Float, default=0)

    __mapper_args__ = {"eager_defaults": True}
