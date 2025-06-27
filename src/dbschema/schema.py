import json
from pydantic import BaseModel

from dbschema.table import Table


class Schema(BaseModel):

    tables: list[Table] = []

    @classmethod
    def get_table_from_metadata(schema_metadata, name: str) -> Table | None:
        """
        Retrieves a table from the schema metadata by its name.
        Args:
            schema_metadata: The metadata of the schema containing the tables.
            name: The name of the table to retrieve.
        Returns:
            Table: The table object if found, otherwise None.
        """
        for table_name, table_metadata in schema_metadata.tables.items():
            if table_name.lower() == name.lower():
                return Table.from_metadata(table_metadata)
        return None

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

    def save(self, json_file: str):
        """
        Guarda el esquema en un archivo JSON.
        :param file_path: Ruta del archivo donde se guardará el esquema.
        """
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(), f, indent=4, ensure_ascii=False)