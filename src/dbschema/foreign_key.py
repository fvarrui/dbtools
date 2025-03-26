from dataclasses import dataclass, asdict

@dataclass
class ForeignKey:

    column : str = None
    references : dict = None

    def __init__(self, metadata: any):
        self.column = metadata.parent.name
        self.references = {
            "table": metadata.column.table.name,
            "column": metadata.column.name
        }

    def __str__(self):
        return f"{self.column} -> {self.references['table']}.{self.references['column']}"
    
    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        return asdict(self)