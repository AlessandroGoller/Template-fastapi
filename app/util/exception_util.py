class EntityDoesNotExistError(Exception):
    """
    Throw an exception when the data does not exist in the database.
    """


class EntityAlreadyExistsError(Exception):
    """
    Throw an exception when the data already exist in the database.
    """
