from pydantic import BaseModel

from dbschema.table import Table


class Schema(BaseModel):

    tables: list[Table] = []

    @classmethod
    def from_metadata(cls, metadata: any, table_names: list[str] = None) -> "Schema":
        tables = []
        for table_name, table_metadata in metadata.tables.items():
            if table_names and table_name not in table_names:
                continue
            tables.append(Table.from_metadata(table_metadata))
        return cls(tables=tables)
