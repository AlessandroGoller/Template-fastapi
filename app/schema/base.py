import datetime
from typing import Any, Dict, Type, TypeVar

from pydantic import BaseModel, ConfigDict

from app.util.datetime_util import format_datetime_into_isoformat

T = TypeVar("T", bound="BaseSchemaModel")

class BaseSchemaModel(BaseModel):
    """
    Base class for schema models.

    This class provides configuration options for Pydantic models used as schemas
    and includes support for automatic SQLAlchemy model conversion.
    """

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        populate_by_name=True,
        json_encoders={datetime.datetime: format_datetime_into_isoformat},
    )

    @classmethod
    def from_orm(cls: Type[T], obj: Any) -> T:
        """
        Create a model instance from a SQLAlchemy model.

        This method safely extracts column values from SQLAlchemy models
        to avoid type errors with Column objects.

        Args:
            obj: SQLAlchemy model instance

        Returns:
            Pydantic model instance populated with values from the SQLAlchemy model
        """
        if obj is None:
            raise Exception("Object cannot be None")

        # Handle SQLAlchemy models that have __table__ attribute
        if hasattr(obj, "__table__"):
            # Extract actual values from SQLAlchemy columns
            obj_dict = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            return cls.model_validate(obj_dict)

        # For other objects, use the standard Pydantic conversion
        return cls.model_validate(obj)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to a dictionary.

        Returns:
            Dictionary representation of the model
        """
        return self.model_dump()
