from pydantic import BaseModel

from dbschema.table import Table

class Schema(BaseModel):

    tables: list[Table] = []

    @classmethod
    def from_metadata(cls, metadata: any, prefix: str = None):
        tables = []
        for table_name, table_metadata in metadata.tables.items():
            if prefix and not table_name.startswith(prefix):
                continue
            tables.append(Table.from_metadata(table_metadata))
        return cls(
            tables=tables
        )
