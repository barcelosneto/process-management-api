from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import Owner, Process, Movement

class ProcessRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, process_id: int):
        process = self.session.get(Process, process_id)
        return process if process and not process.deleted else None

    def list(self, status: str | None, owner_id: int | None, due_before: date | None):
        query = select(Process).where(Process.deleted.is_(False)).order_by(Process.id)
        if status:
            query = query.where(Process.status == status)
        if owner_id is not None:
            query = query.where(Process.owner_id == owner_id)
        if due_before:
            query = query.where(Process.due_date <= due_before)
        return self.session.scalars(query).all()

    def owner_exists(self, owner_id: int):
        return self.session.get(Owner, owner_id) is not None

    def history(self, process_id: int):
        return self.session.scalars(select(Movement).where(Movement.process_id == process_id).order_by(Movement.id)).all()
