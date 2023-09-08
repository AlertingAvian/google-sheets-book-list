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


class InvalidISBNError(Exception):
    """
        Exception raised if provided ISBN is invalid

        Attributes:
            isbn -- the invalid isbn
        """

    def __init__(self, isbn: str = ""):
        self.isbn = isbn
        self.message = \
            f'Invalid {"ISBN: " + isbn if isbn else "ISBN"}.'
        super().__init__(self.message)
