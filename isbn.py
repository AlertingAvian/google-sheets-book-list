from isbnlib import notisbn, canonical, meta, desc

import exceptions
from models import BookData


def validate_isbn(isbnlike: any) -> bool:
    return not notisbn(isbnlike, level='strict')


def get_data(isbnlike: any) -> BookData:
    if not validate_isbn(isbnlike):
        raise exceptions.InvalidISBNError(isbnlike)
    isbn = canonical(isbnlike)
    data = meta(isbn)
    description = desc(isbn)
    if not data:
        raise exceptions.NoDataError(isbn)
    return BookData(
        Title=data["Title"],
        Authors=data["Authors"],
        Year=data["Year"],
        Publisher=data["Publisher"],
        Description=description,
        ISBN=data["ISBN-13"]
    )
