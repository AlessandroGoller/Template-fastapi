from loguru import logger


def define_logger() -> None:
    """
    Configures the application logger with specific settings.

    This function sets up a logger to write log messages to a file with the following configurations:
    - Log file path: "logs/app.log"
    - Log rotation: The log file is rotated after reaching 10 MB in size.
    - Log retention: Rotated log files are kept for 7 days.
    - Log compression: Rotated log files are compressed using the ZIP format.
    - Log level: Only messages with a severity level of INFO or higher are logged.

    Returns:
        None
    """
    logger.add("logs/app.log",
           rotation="10 MB",      # Rotate after 10MB
           retention="7 days",    # Keep logs for 7 days
           compression="zip",     # Compress rotated logs
           level="INFO")
