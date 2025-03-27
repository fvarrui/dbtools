from pydantic import BaseModel

from dbschema.reference import Reference

class ForeignKey(BaseModel):

    column : str
    reference : Reference

    @classmethod
    def from_metadata(cls, fk_metadata: any):
        return cls(
            column = fk_metadata.parent.name,
            reference = Reference.from_metadata(fk_metadata)
        )

    def __str__(self):
        return f"{self.column} -> {self.reference}"
    
    def __repr__(self):
        return self.__str__()
