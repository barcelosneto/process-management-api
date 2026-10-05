import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.database import Base, engine
from app.routes.processes import router
from app.services.processes import DomainError

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(title="Process Management API", lifespan=lifespan)
app.include_router(router)

@app.exception_handler(DomainError)
async def domain_error(request: Request, error: DomainError):
    return JSONResponse(status_code=error.status, content={"detail": error.message})

@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, error: SQLAlchemyError):
    logging.getLogger(__name__).exception("Database operation failed")
    return JSONResponse(status_code=500, content={"detail": "Database operation failed"})
