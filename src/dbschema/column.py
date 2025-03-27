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
        return self.name == value.name and self.type == value.type
