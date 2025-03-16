from tabulate import tabulate
from textwrap import shorten
from .column import Column
from .foreign_key import ForeignKey

class Table:
    
    name : str = None
    description : str = None
    columns : Column = []
    primary_keys : list[str] = []
    foreign_keys : ForeignKey = []

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