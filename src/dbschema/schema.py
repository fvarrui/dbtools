import json
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

    @staticmethod
    def from_json(json_path: str) -> "Schema":
        with open(json_path, "r", encoding="utf-8") as f:
            schema_json = json.load(f)
        return Schema.model_validate(schema_json["schema"])

    def to_json(self, indent=4, separators=None) -> str:
        schema_dict = self.model_dump()
        return json.dumps(schema_dict, indent=indent, separators=separators)

    def reduce(self) -> dict:
        return {
            table.name: {
                "columns": {
                    column.name: (
                        f"{column.type} NOT NULL"
                        if not column.nullable
                        else column.type
                    )
                    for column in table.columns
                },
                "primary_keys": table.primary_keys,
                "foreign_keys": {
                    fk.column: f"{fk.reference.table}.{fk.reference.column}"
                    for fk in table.foreign_keys
                },
            }
            for table in self.tables
        }
