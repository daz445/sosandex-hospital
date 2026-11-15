import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from app.database import init_db
from app.routers.doctors import router as doctors_router
from app.routers.patients import router as patients_router
from app.routers.appointments import router as appointments_router
from app.routers.pages import router as pages_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Муниципальная Городская Больница",
    lifespan=lifespan,
)

BASE = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE, "templates"))
app.state.templates = templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE, "static")), name="static")

app.include_router(doctors_router)
app.include_router(patients_router)
app.include_router(appointments_router)
app.include_router(pages_router)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Нарушение целостности данных (например, удаление врача,
    у которого есть записи на приём) -> 409 Conflict, а не 500."""
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Конфликт данных: операция нарушает целостность базы "
                      "(возможно, есть связанные записи). Изменение отменено."
        },
    )
