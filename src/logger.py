from functools import wraps

from fastlogging import LogInit
from flask import request

from src.config import Config

class Logger:
    def __init__(self, filename="devika_agent.log"):
        """        Initialize the logger with the specified filename.

        Args:
            filename (str): The name of the log file. Defaults to "devika_agent.log".
        """

        config = Config()
        logs_dir = config.get_logs_dir()
        self.logger = LogInit(pathName=logs_dir + "/" + filename, console=True, colors=True)

    def read_log_file(self) -> str:
        """        Read the contents of the log file.

        Opens the log file in read mode and returns its contents as a string.

        Returns:
            str: The contents of the log file.

        Raises:
            FileNotFoundError: If the log file specified by self.logger.pathName does not exist.
        """

        with open(self.logger.pathName, "r") as file:
            return file.read()

    def info(self, message: str):
        """        Log an informational message.

        This method logs an informational message using the provided message string.

        Args:
            message (str): The message to be logged.
        """

        self.logger.info(message)
        self.logger.flush()

    def error(self, message: str):
        """        Log an error message and flush the logger.

        Args:
            message (str): The error message to be logged.
        """

        self.logger.error(message)
        self.logger.flush()

    def warning(self, message: str):
        """        Log a warning message and flush the logger.

        Args:
            message (str): The warning message to be logged.
        """

        self.logger.warning(message)
        self.logger.flush()

    def debug(self, message: str):
        """        Log a debug message.

        This method logs a debug message using the provided message string and then flushes the logger.

        Args:
            message (str): The message to be logged.
        """

        self.logger.debug(message)
        self.logger.flush()

    def exception(self, message: str):
        """        Log an exception message and flush the logger.

        Args:
            message (str): The exception message to be logged.
        """

        self.logger.exception(message)
        self.logger.flush()


def route_logger(logger: Logger):
    """    Decorator factory that creates a decorator to log route entry and exit points.
    The decorator uses the provided logger to log the information.

    Args:
        logger (Logger): The logger instance to use for logging.

    Returns:
        function: A decorator function that logs route entry and exit points.
    """

    log_enabled = Config().get_logging_rest_api()

    def decorator(func):
        """        Decorator for logging entry and exit points of a route function.

        This decorator logs the entry point of the route function, calls the actual route function, and then logs the exit point,
        including the response summary if possible.

        Args:
            func (function): The route function to be decorated.

        Returns:
            function: The decorated route function.

        Raises:
            Exception: If an error occurs while logging the exit point.
        """


        @wraps(func)
        def wrapper(*args, **kwargs):
            """            Log entry point and call the actual route function. Log exit point, including response summary if possible.

            Args:
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                object: The response from the route function.
            """

            # Log entry point
            if log_enabled:
                logger.info(f"{request.path} {request.method}")

            # Call the actual route function
            response = func(*args, **kwargs)

            # Log exit point, including response summary if possible
            try:
                if log_enabled:
                    response_summary = response.get_data(as_text=True)
                    logger.debug(f"{request.path} {request.method} - Response: {response_summary}")
            except Exception as e:
                logger.exception(f"{request.path} {request.method} - {e})")

            return response
        return wrapper
    return decorator
