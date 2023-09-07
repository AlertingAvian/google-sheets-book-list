class NoDataError(Exception):
    """
    Exception raised if data lookup returns no information

    Attributes:
        isbn -- isbn of the lookup that caused the error
    """

    def __init__(self, isbn: str = ""):
        self.isbn = isbn
        self.message = \
            f'Error {"while looking up ISBN: " + isbn if isbn else "while attempting ISBN lookup"}. No Data found.'
        super().__init__(self.message)
