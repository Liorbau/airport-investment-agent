"""Chat messages and the events the agent streams: progress steps, then one answer."""

from typing import Literal

from pydantic import BaseModel, Field

from app.modules.live_status.schemas import LiveStatus
from app.modules.rankings.schemas import Profiles

MAX_QUESTION_CHARS = 2000
MAX_SPEECH_CHARS = 1000


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_SPEECH_CHARS)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_CHARS)
    history: list[ChatMessage] = []


class ToolCall(BaseModel):
    name: str
    arguments: str
    output: str


class Progress(BaseModel):
    type: Literal["progress"] = "progress"
    message: str


class NumberCheck(BaseModel):
    numbers_checked: int
    unverified_numbers: list[str]


class Answer(BaseModel):
    type: Literal["answer"] = "answer"
    text: str
    tool_calls: list[ToolCall]
    steps: int
    number_check: NumberCheck


class ChatError(BaseModel):
    type: Literal["error"] = "error"
    message: str


class AirportDetails(BaseModel):
    statistics: Profiles
    live_status: LiveStatus
