from pydantic import BaseModel
from typing import Any

class MatchResult(BaseModel):

    matches: list[Any]
    unmatched_srcs: list[Any]
    unmatched_dsts: list[Any]

    @classmethod
    def create(cls, matches: list, unmatched_srcs: list, unmatched_dsts: list) -> "MatchResult":
        return cls(
            matches=matches,
            unmatched_srcs=unmatched_srcs,
            unmatched_dsts=unmatched_dsts
        )
