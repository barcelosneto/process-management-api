import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()
url = os.getenv("DATABASE_URL", "sqlite:///./processes.db")
engine = create_engine(url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {})
if url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_session():
    with SessionLocal() as session:
        yield session
