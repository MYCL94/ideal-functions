class CustomError(Exception):
    """
    A custom exception class.
    """

    def __init__(self, message, error_code=None) -> None:
        """
        Initialize the custom exception.

        Args:
            message (str): The error message.
            error_code (int, optional): An optional error code. Defaults to None.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        """
        Return a string representation of the exception.
        """
        if self.error_code:
            return f"CustomError: {self.message} (Error Code: {self.error_code})"
        else:
            return f"CustomError: {self.message}"