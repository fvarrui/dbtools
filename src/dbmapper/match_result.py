from pydantic import BaseModel
from typing import Any

from dbmapper.score import Score

class MatchResult(BaseModel):

    matched: list[Score]
    unmatched_srcs: list[Any]
    unmatched_dsts: list[Any]

    @classmethod
    def create(cls, matched: list[Score], unmatched_srcs: list, unmatched_dsts: list) -> "MatchResult":
        return cls(
            matched=matched,
            unmatched_srcs=unmatched_srcs,
            unmatched_dsts=unmatched_dsts
        )
