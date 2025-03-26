from dataclasses import dataclass, asdict, field

from .database import Database
from .table import Table

@dataclass
class Schema:

    database: Database
    tables: list[Table] = field(default_factory=list)

    def __init__(self, database: Database, tables: list[Table]):
        self.database = database
        self.tables = tables

    def __dict__(self):
        return asdict(self)