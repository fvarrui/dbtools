from pydantic import BaseModel
from tabulate import tabulate
from textwrap import shorten
from typing import Optional

from dbschema.column import Column
from dbschema.foreign_key import ForeignKey


class Table(BaseModel):

    name: str
    comment: Optional[str]
    columns: list[Column] = []
    primary_keys: list[str] = []
    foreign_keys: list[ForeignKey] = []
    schemaName: Optional[str]

    @classmethod
    def from_metadata(cls, table_metadata: any):
        return cls(
            name=table_metadata.name,
            comment=table_metadata.comment,
            columns=[
                Column.from_metadata(column_metadata)
                for column_metadata in table_metadata.columns
            ],
            primary_keys=[
                column_metadata.name
                for column_metadata in table_metadata.primary_key.columns
            ],
            foreign_keys=[
                ForeignKey.from_metadata(fk_metadata)
                for fk_metadata in table_metadata.foreign_keys
            ],
            schemaName=None
        )
    
    def search_columns(self, search_term: str):
        return [ column for column in self.columns if search_term.lower() in column.name.lower() or search_term.lower() in (column.comment or '').lower() ]
    
    def __lt__(self, other):
        if not isinstance(other, Table):
            return NotImplemented
        return self.name < other.name
    
    def __str__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, value):
        if not isinstance(value, Table):
            return NotImplemented
        return self.name == value.name
    
    def print(self):
        fks = set()
        for fk in self.foreign_keys:
            fks.add(fk.column)
        print("Tabla           :", self.name)
        print("Descripción     :", self.comment if self.comment else "")
        print("Clave primaria  :", ", ".join(self.primary_keys) if self.primary_keys else "Ninguna")
        print("Claves foráneas :", ", ".join(fks) if fks else "Ninguna")
        headers = ["PK", "COLUMN_NAME", "TYPE", "NULLABLE", "RELATION", "COMMENT"]
        data = []
        for column in self.columns:
            type = column.type
            is_pk = "🔑" if column.name in self.primary_keys else "❌"
            is_nullable = "✅" if column.nullable else "❌"
            relations = []
            for fk in self.foreign_keys:
                if column.name == fk.column:
                    relations.append(f"{fk.reference}")
            data.append(
                [
                    is_pk,
                    column.name,
                    type,
                    is_nullable,
                    "\n".join(relations),
                    shorten(
                        column.comment if column.comment else "",
                        width=100,
                        placeholder="...",
                    ),
                ]
            )
        print(tabulate(data, headers=headers, tablefmt="grid"))
