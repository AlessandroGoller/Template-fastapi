import datetime


def format_datetime_into_isoformat(date_time: datetime.datetime) -> str:
    """
    Formats a datetime object into ISO 8601 format.

    Args:
        date_time (datetime.datetime): The datetime object to be formatted.

    Returns:
        str: The formatted datetime string in ISO 8601 format.

    """
    return (
        date_time.replace(tzinfo=datetime.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
