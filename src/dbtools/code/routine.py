from pydantic import BaseModel
from typing import Optional, Literal

RoutineType = Literal["PROCEDURE", "FUNCTION"]


class Routine(BaseModel):

    name: str
    type: RoutineType
    schema_name: Optional[str] = None
    language: Optional[str] = None
    return_type: Optional[str] = None
    definition: Optional[str] = None

    def to_sql(self) -> str:
        """
        Devuelve la definición SQL del procedimiento o función.
        """
        return self.definition or ""

    def __lt__(self, other):
        if not isinstance(other, Routine):
            return NotImplemented
        return (self.type, self.name) < (other.type, other.name)

    def __str__(self):
        return f"{self.type} {self.name}"
