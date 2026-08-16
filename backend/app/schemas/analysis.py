from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.graph import GraphResponse


class AnalysisCreateRequest(BaseModel):
    query_input: str = Field(
        ..., min_length=3, description="URL, headline or short description of the story"
    )


class AnalysisCreateResponse(BaseModel):
    analysis_id: str
    status: str


class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    status: str
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class AnalysisResultResponse(AnalysisStatusResponse):
    graph: GraphResponse | None = None
