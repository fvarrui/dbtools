class Column:

    def __init__(self, name: str, sql_type: str, max_length: int, nullable: bool):
        self.name = name
        self.type = self.__prettify_type(sql_type, max_length)
        self.max_length = max_length
        self.nullable = nullable
        self.is_primary_key = False
        self.description = None
        self.relation = None

    def __eq__(self, value):
        return self.name == value.name and self.type == value.type

    def __prettify_type(self, type : str, max_length : int) -> str:
        match type:
            case "int" | "tinyint" | "smallint" | "bigint":
                return "integer"
            case "decimal" | "numeric":
                return "float"
            case "varchar" | "nvarchar" | "char":
                return f"string"
            case "bit" if max_length == 1:
                return "boolean"
            case "datetime" | "smalldatetime":
                return "datetime"
            case _:
                return type
