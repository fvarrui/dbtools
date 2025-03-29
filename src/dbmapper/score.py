from pydantic import BaseModel
from typing import Any

class Score(BaseModel):

    src: Any
    dst: Any
    ratio: float
    data: dict[str, Any] = {}

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
        return f"{self.src} -> {self.dst} ({self.ratio:.2f})"

    def __eq__(self, value):
        if not isinstance(value, Score):
            return NotImplemented
        return self.src == value.src and self.dst == value.dst
    
    def __hash__(self):
        return hash((self.src, self.dst))

    class Config:
        arbitrary_types_allowed = True  # Permitir tipos arbitrarios
