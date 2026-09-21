from datetime import date
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.database_models import Doctor, Patient, Appointment, AppointmentStatus

router = APIRouter(tags=["pages"])


@router.get("/")
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    today = date.today()
    doctors_count = (await db.execute(select(func.count(Doctor.id)))).scalar() or 0
    patients_count = (await db.execute(select(func.count(Patient.id)))).scalar() or 0
    appointments_today = (await db.execute(
        select(func.count(Appointment.id)).where(
            Appointment.appointment_date == today,
            Appointment.status == AppointmentStatus.BOOKED,
        )
    )).scalar() or 0
    return request.app.state.templates.TemplateResponse("index.html", {
        "request": request, "page": "index",
        "doctors_count": doctors_count, "patients_count": patients_count,
        "appointments_today": appointments_today, "today": today,
    })


@router.get("/schedule")
async def schedule_page(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Doctor).options(selectinload(Doctor.schedule_slots)).order_by(Doctor.last_name)
    )
    doctors = result.scalars().all()
    return request.app.state.templates.TemplateResponse("schedule.html", {
        "request": request, "page": "schedule", "doctors": doctors,
        "today": date.today(),
        "weekday_names": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
    })


@router.get("/doctors")
async def doctors_page(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Doctor).order_by(Doctor.last_name))
    doctors = result.scalars().all()
    return request.app.state.templates.TemplateResponse("doctors.html", {
        "request": request, "page": "doctors", "doctors": doctors,
    })


@router.get("/patients")
async def patients_page(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).order_by(Patient.last_name))
    patients = result.scalars().all()
    return request.app.state.templates.TemplateResponse("patients.html", {
        "request": request, "page": "patients", "patients": patients,
    })


@router.get("/appointments")
async def appointments_page(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Appointment)
        .options(selectinload(Appointment.doctor), selectinload(Appointment.patient))
        .order_by(Appointment.appointment_date, Appointment.start_time)
    )
    appointments = result.scalars().all()
    return request.app.state.templates.TemplateResponse("appointments.html", {
        "request": request, "page": "appointments", "appointments": appointments,
    })


@router.get("/admin")
async def admin_page(request: Request, db: AsyncSession = Depends(get_db)):
    doctors_count = (await db.execute(select(func.count(Doctor.id)))).scalar() or 0
    patients_count = (await db.execute(select(func.count(Patient.id)))).scalar() or 0
    appointments_count = (await db.execute(select(func.count(Appointment.id)))).scalar() or 0
    booked_count = (await db.execute(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.BOOKED)
    )).scalar() or 0
    return request.app.state.templates.TemplateResponse("admin/dashboard.html", {
        "request": request, "page": "admin",
        "doctors_count": doctors_count, "patients_count": patients_count,
        "appointments_count": appointments_count, "booked_count": booked_count,
    })
