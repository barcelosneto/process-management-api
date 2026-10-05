from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class OwnerInput(BaseModel):
    name: str = Field(min_length=1, max_length=120, pattern=r".*\S.*")

class OwnerOutput(OwnerInput):
    model_config = ConfigDict(from_attributes=True)
    id: int

class ProcessInput(BaseModel):
    title: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
    owner_id: int = Field(gt=0)
    status: Literal["open", "in_progress", "completed"] = "open"
    start_date: date
    due_date: date
    sla_days: int = Field(gt=0, le=3650)
    completed_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.due_date < self.start_date:
            raise ValueError("due_date must not precede start_date")
        if (self.status == "completed") != (self.completed_date is not None):
            raise ValueError("completed status requires completed_date; active status forbids it")
        if self.completed_date and (self.completed_date < self.start_date or self.completed_date > date.today()):
            raise ValueError("completed_date must be between start_date and today")
        return self

class ProcessOutput(ProcessInput):
    id: int
    days_until_due: int
    overdue: bool
    outside_sla: bool

class MovementInput(BaseModel):
    description: str = Field(min_length=1, max_length=1000, pattern=r".*\S.*")

class MovementOutput(MovementInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    process_id: int
    created_at: datetime
