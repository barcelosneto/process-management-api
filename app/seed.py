from datetime import date, timedelta
from sqlalchemy import select
from app.database import Base, engine, SessionLocal
from app.models.entities import Owner
from app.services.processes import ProcessService
from app.schemas.processes import ProcessInput

def main():
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        if session.scalar(select(Owner.id).limit(1)) is not None:
            print("Seed skipped: database already has owners")
            return
        owner = Owner(name="Responsible FICTITIOUS A")
        session.add(owner)
        session.commit()
        today = date.today()
        for index, due in enumerate([today - timedelta(days=2), today + timedelta(days=4)]):
            ProcessService(session).save(ProcessInput(title=f"FICTITIOUS process {index + 1}", owner_id=owner.id,
                start_date=today - timedelta(days=10), due_date=due, sla_days=7))
        print("Two fictional processes created")

if __name__ == "__main__":
    main()
