from dataclasses import dataclass, field, asdict
from tabulate import tabulate
from textwrap import shorten
from .column import Column
from .foreign_key import ForeignKey

@dataclass
class Table:
    
    name : str = None
    comment : str = None
    columns : list[Column] = field(default_factory=list)
    primary_keys : list[str] = field(default_factory=list)
    foreign_keys : list[ForeignKey] = field(default_factory=list)

    def __init__(self, metadata: any):
        self.name = metadata.name
        self.comment = metadata.comment
        self.columns = [ Column(column) for column in metadata.columns ]
        self.primary_keys = [ column.name for column in metadata.primary_key.columns ]
        self.foreign_keys = [ ForeignKey(fk) for fk in metadata.foreign_keys ]

    def print(self):
        print("Tabla       :", self.name)
        print("Descripción :", self.description)
        headers = [ "PK", "COLUMN_NAME", "TYPE", "NOT_NULLABLE", "RELATION", "DESCRIPTION" ]
        data = []
        for column in self.columns:
            type = column.type if column.max_length is None else f"{column.type}({column.max_length})"
            is_pk = "X" if column.is_primary_key else ""
            is_not_nullable = "X" if column.nullable == "NO" else ""
            relation = f"{column.relation.referenced_table}.{column.relation.referenced_column}" if column.relation else ""
            data.append([ is_pk, column.name, type, is_not_nullable, relation, shorten(column.description, width=100, placeholder="...") ])
        print(tabulate(data, headers=headers, tablefmt="grid"))

    def __dict__(self):
        return asdict(self)