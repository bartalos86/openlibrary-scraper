from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Link:
    book_id: str
    url: str
    parent: str
    date_accessed: datetime = field(default_factory=datetime.now)
