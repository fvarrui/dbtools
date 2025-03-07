from tabulate import tabulate
from textwrap import shorten
from .column import Column

class View:
    
    name : str = None
    columns : Column = []

    def print(self):
        print("Vista:", self.name)
        headers = [ "COLUMN_NAME", "TYPE", "NOT_NULLABLE", "DESCRIPTION" ]
        data = []
        for column in self.columns:
            is_not_nullable = "X" if column.nullable == "NO" else ""
            data.append([ column.name, column.type, is_not_nullable, shorten(column.description, width=100, placeholder="...") ])
        print(tabulate(data, headers=headers, tablefmt="grid"))

