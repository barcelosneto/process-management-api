from datetime import date
from typing import Literal
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_session
from app.models.entities import Owner
from app.schemas.processes import OwnerInput, OwnerOutput, ProcessInput, ProcessOutput, MovementInput, MovementOutput
from app.services.processes import ProcessService, present

router = APIRouter()

@router.post("/owners", response_model=OwnerOutput, status_code=201)
def create_owner(data: OwnerInput, session: Session = Depends(get_session)):
    owner = Owner(**data.model_dump())
    session.add(owner)
    session.commit()
    session.refresh(owner)
    return owner

@router.get("/owners", response_model=list[OwnerOutput])
def list_owners(session: Session = Depends(get_session)):
    return session.scalars(select(Owner).order_by(Owner.id)).all()

@router.get("/processes", response_model=list[ProcessOutput])
def list_processes(status: Literal["open", "in_progress", "completed"] | None = None,
                   owner_id: int | None = Query(None, gt=0), due_before: date | None = None,
                   overdue: bool | None = None, session: Session = Depends(get_session)):
    items = [present(item) for item in ProcessService(session).repository.list(status, owner_id, due_before)]
    return [item for item in items if overdue is None or item.overdue == overdue]

@router.get("/indicators")
def indicators(session: Session = Depends(get_session)):
    items = [present(item) for item in ProcessService(session).repository.list(None, None, None)]
    return {"total": len(items), "overdue": sum(item.overdue for item in items),
            "outside_sla": sum(item.outside_sla for item in items),
            "by_status": {state: sum(item.status == state for item in items) for state in ["open", "in_progress", "completed"]}}

@router.post("/processes", response_model=ProcessOutput, status_code=201)
def create_process(data: ProcessInput, session: Session = Depends(get_session)):
    return ProcessService(session).save(data)

@router.get("/processes/{process_id}", response_model=ProcessOutput)
def get_process(process_id: int, session: Session = Depends(get_session)):
    return present(ProcessService(session).require(process_id))

@router.put("/processes/{process_id}", response_model=ProcessOutput)
def update_process(process_id: int, data: ProcessInput, session: Session = Depends(get_session)):
    return ProcessService(session).save(data, process_id)

@router.delete("/processes/{process_id}", status_code=204)
def delete_process(process_id: int, session: Session = Depends(get_session)):
    ProcessService(session).delete(process_id)
    return Response(status_code=204)

@router.get("/processes/{process_id}/movements", response_model=list[MovementOutput])
def history(process_id: int, session: Session = Depends(get_session)):
    service = ProcessService(session)
    service.require(process_id)
    return service.repository.history(process_id)

@router.post("/processes/{process_id}/movements", response_model=MovementOutput, status_code=201)
def add_movement(process_id: int, data: MovementInput, session: Session = Depends(get_session)):
    return ProcessService(session).add_movement(process_id, data.description)
