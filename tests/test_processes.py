from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_session
from app.main import app
from app.models.entities import Process
from app.services.processes import present

@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    def override():
        with factory() as session:
            yield session
    app.dependency_overrides[get_session] = override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    engine.dispose()

def payload():
    return dict(title="FICTITIOUS task", owner_id=1, start_date="2020-01-01", due_date="2020-01-10", sla_days=5)

def test_crud_history_filters_and_indicators(client):
    assert client.post("/owners", json={"name": "FICTITIOUS A"}).status_code == 201
    response = client.post("/processes", json=payload())
    assert response.status_code == 201
    assert response.json()["overdue"] is True
    data = payload() | {"status": "completed", "completed_date": "2020-01-04"}
    assert client.put("/processes/1", json=data).json()["outside_sla"] is False
    assert len(client.get("/processes?status=completed&owner_id=1&due_before=2020-01-10").json()) == 1
    assert client.post("/processes/1/movements", json={"description": "FICTITIOUS review"}).status_code == 201
    assert len(client.get("/processes/1/movements").json()) == 3
    assert client.get("/indicators").json()["total"] == 1
    assert client.delete("/processes/1").status_code == 204
    assert client.get("/processes/1").status_code == 404
    assert client.get("/indicators").json()["total"] == 0

@pytest.mark.parametrize("changes", [{"due_date": "2019-01-01"}, {"sla_days": 0}, {"status": "completed"}, {"title": "   "}, {"completed_date": "2020-01-04"}])
def test_invalid_input(client, changes):
    assert client.post("/processes", json=payload() | changes).status_code == 422

def test_missing_owner(client):
    assert client.post("/processes", json=payload()).status_code == 404

def test_sla_boundary_and_completion():
    process = Process(id=1, title="FICTITIOUS", owner_id=1, status="open", start_date=date(2020,1,1), due_date=date(2020,1,6), sla_days=5)
    assert not present(process, date(2020,1,6)).outside_sla
    assert not present(process, date(2020,1,6)).overdue
    assert present(process, date(2020,1,7)).outside_sla
    process.status, process.completed_date = "completed", date(2020,1,5)
    assert not present(process, date(2025,1,1)).overdue
