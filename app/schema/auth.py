from pydantic import EmailStr

from app.schema.base import BaseSchemaModel


class AuthSchema(BaseSchemaModel):
    """
    Schema for signing in a user.

    Attributes:
        email (str): The email of the user.
        password (str): The password of the user.
    """

    email: EmailStr
    password: str

    class Config:
        """
        Config:
            json_schema_extra (dict): Extra schema information.
                example (dict): An example of the schema data.
                    email (str): Example email.
                    password (str): Example password.
        """

        json_schema_extra = {
            "example": {"email": "fake.email@gmail.com", "password": "password"},
        }
