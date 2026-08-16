from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.graph.builder import build_graph_response
from app.models.models import Analysis, AnalysisStatus
from app.pipeline.orchestrator import run_analysis
from app.queue import get_queue
from app.schemas.analysis import (
    AnalysisCreateRequest,
    AnalysisCreateResponse,
    AnalysisResultResponse,
)

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("", response_model=AnalysisCreateResponse, status_code=202)
def create_analysis(payload: AnalysisCreateRequest, db: Session = Depends(get_db)):
    analysis = Analysis(query_input=payload.query_input.strip())
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    queue = get_queue()
    queue.enqueue(run_analysis, analysis.id, job_id=analysis.id)

    return AnalysisCreateResponse(analysis_id=analysis.id, status=analysis.status.value)


@router.get("/{analysis_id}", response_model=AnalysisResultResponse)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    graph = build_graph_response(analysis) if analysis.status == AnalysisStatus.DONE else None

    return AnalysisResultResponse(
        analysis_id=analysis.id,
        status=analysis.status.value,
        error=analysis.error,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
        graph=graph,
    )
