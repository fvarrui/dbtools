from pydantic import BaseModel

class Reference(BaseModel):

    table: str
    column : str

    @classmethod
    def from_metadata(cls, column_metadata: any):
        return cls(
            table = column_metadata.table.name,
            column = column_metadata.name
        )

    def __str__(self):
        return f"{self.table}.{self.column}"
    
    def __repr__(self):
        return self.__str__()
