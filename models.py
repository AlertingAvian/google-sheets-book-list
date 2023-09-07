from dataclasses import dataclass
from typing import List


@dataclass
class BookData:
    Title: str
    Authors: List[str]
    Year: str
    Publisher: str
    Description: str
    ISBN: str
