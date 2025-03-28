from pydantic import BaseModel
from typing import Any

class Score(BaseModel):

    src: Any
    dst: Any
    ratio: float

    @classmethod
    def create(cls, src, dst, ratio: float = 0.0) -> "Score":
        return cls(
            src=src,
            dst=dst,
            ratio=ratio
        )

    def __compare__(self, other):
        return self.ratio - other.ratio
    
    def __str__(self):
        return f"{self.src.name} -> {self.dst.name} ({self.ratio})"

    class Config:
        arbitrary_types_allowed = True  # Permitir tipos arbitrarios
