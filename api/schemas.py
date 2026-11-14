from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = Field(default=None, max_length=64)

    @field_validator("message")
    @classmethod
    def not_blank(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("message is empty")
        return v


class Source(BaseModel):
    n: int
    scheme_id: str
    scheme_name: str
    section: str
    file: str
    snippet: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    kind: str
    route: str
    language: str
    sources: list[Source] = []
    verdicts: dict[str, str] = {}
    latency_s: float


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., max_length=64)
    rating: Literal["up", "down"]
    message: str = Field(default="", max_length=500)
    reply: str = Field(default="", max_length=4000)
    comment: str = Field(default="", max_length=500)