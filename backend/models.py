"""Data models — LangGraph states (TypedDict) + API models (Pydantic)."""
from __future__ import annotations

from enum import Enum
from typing import Annotated, TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import add_messages


# ── Enums ──

class InterviewMode(str, Enum):
    RESUME = "resume"
    TOPIC_DRILL = "topic_drill"
    JD_PREP = "jd_prep"
    RECORDING = "recording"


class InterviewPhase(str, Enum):
    GREETING = "greeting"
    SELF_INTRO = "self_intro"
    TECHNICAL = "technical"
    PROJECT_DEEP_DIVE = "project_deep_dive"
    REVERSE_QA = "reverse_qa"
    END = "end"


# ── LangGraph States (TypedDict for max compatibility) ──

class ResumeInterviewState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    phase: str           # InterviewPhase value
    resume_context: str
    questions_asked: list[str]
    phase_question_count: int
    is_finished: bool
    last_eval: dict          # Latest inline eval from interviewer {score, should_advance, brief}
    eval_history: list       # All evals accumulated across the interview


class TopicDrillState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    topic: str
    topic_name: str
    knowledge_context: str
    difficulty: int
    questions_asked: list[str]
    scores: list[dict]
    weak_points: list[str]
    total_questions: int
    is_finished: bool


# ── API Models (Pydantic) ──

class StartInterviewRequest(BaseModel):
    mode: InterviewMode
    topic: str | None = None


class JobPrepPreviewRequest(BaseModel):
    jd_text: str
    company: str | None = None
    position: str | None = None
    use_resume: bool = True


class JobPrepStartRequest(JobPrepPreviewRequest):
    preview_data: dict | None = None


class ChatRequest(BaseModel):
    session_id: str
    message: str


class EndDrillRequest(BaseModel):
    answers: list[dict] = Field(default_factory=list)  # [{question_id: int, answer: str}]


class RecordingAnalyzeRequest(BaseModel):
    transcript: str
    recording_mode: str = "dual"  # "dual" | "solo"
    company: str | None = None
    position: str | None = None


# ── Auth Models ──

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class LlmSettingsResponse(BaseModel):
    api_base: str = ""
    model: str = ""
    has_api_key: bool = False
    masked_api_key: str | None = None


class UpdateLlmSettingsRequest(BaseModel):
    api_base: str = ""
    api_key: str = ""
    model: str = ""
    replace_api_key: bool = False


class ValidateLlmSettingsRequest(BaseModel):
    api_base: str = ""
    api_key: str = ""
    model: str = ""


class ValidateLlmSettingsResponse(BaseModel):
    ok: bool
    message: str
    resolved_model: str | None = None
