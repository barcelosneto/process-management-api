from datetime import date
from app.models.entities import Process, Movement
from app.repositories.processes import ProcessRepository
from app.schemas.processes import ProcessInput, ProcessOutput

class DomainError(Exception):
    def __init__(self, message: str, status: int = 400):
        self.message, self.status = message, status

def present(process: Process, today: date | None = None) -> ProcessOutput:
    today = today or date.today()
    reference = process.completed_date or today
    return ProcessOutput(
        **{field: getattr(process, field) for field in ProcessInput.model_fields},
        id=process.id,
        days_until_due=(process.due_date - today).days,
        overdue=reference > process.due_date,
        outside_sla=(reference - process.start_date).days > process.sla_days,
    )

class ProcessService:
    def __init__(self, session):
        self.session = session
        self.repository = ProcessRepository(session)

    def require(self, process_id: int):
        process = self.repository.get(process_id)
        if process is None:
            raise DomainError("Process not found", 404)
        return process

    def save(self, data: ProcessInput, process_id: int | None = None):
        if not self.repository.owner_exists(data.owner_id):
            raise DomainError("Owner not found", 404)
        process = self.require(process_id) if process_id is not None else Process()
        old = {key: str(getattr(process, key, None)) for key in ProcessInput.model_fields}
        for key, value in data.model_dump().items():
            setattr(process, key, value)
        self.session.add(process)
        self.session.flush()
        changes = [f"{key}: {old[key]} -> {value}" for key, value in data.model_dump().items() if old[key] != str(value)]
        self.session.add(Movement(process_id=process.id, description=("Created" if process_id is None else "Updated") + ": " + "; ".join(changes)))
        self.session.commit()
        self.session.refresh(process)
        return present(process)

    def delete(self, process_id: int):
        process = self.require(process_id)
        process.deleted = True
        self.session.add(Movement(process_id=process_id, description="Soft deleted"))
        self.session.commit()

    def add_movement(self, process_id: int, description: str):
        self.require(process_id)
        movement = Movement(process_id=process_id, description=description)
        self.session.add(movement)
        self.session.commit()
        self.session.refresh(movement)
        return movement

