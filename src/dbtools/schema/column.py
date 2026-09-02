from pydantic import BaseModel
from typing import Optional

class Column(BaseModel):

    name: str
    type: str
    nullable: bool
    comment: Optional[str]
    default: Optional[str]

    @classmethod
    def from_metadata(cls, column_metadata: any):
        return cls(
            name = column_metadata.name,
            type = Column.__prettify_type__(column_metadata.type),
            nullable = column_metadata.nullable,
            comment = column_metadata.comment,
            default = column_metadata.default,
        )

    def __lt__(self, other):
        if not isinstance(other, Column):
            return NotImplemented
        return self.name < other.name
    
    @staticmethod
    def __prettify_type__(type):
        pretty = type.__class__.__name__
        match pretty:
            case "BIT":
                return "BOOLEAN"
            case "VARCHAR":
                return f"{pretty}({type.length})"
            case _:
                return pretty

    def __eq__(self, value):
        if not isinstance(value, Column):
            return NotImplemented
        return self.name == value.name
    
    def __str__(self):
        return f"{self.name}[{self.type}]"
    
    def __hash__(self):
        return hash(self.name)
