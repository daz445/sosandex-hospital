from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.database_models import Appointment, AppointmentStatus, ScheduleSlot
from app.models.schemas import AppointmentCreate, AppointmentRead

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.get("/", response_model=list[AppointmentRead])
async def list_appointments(
    doctor_id: int | None = None,
    patient_id: int | None = None,
    on_date: date | None = Query(None, alias="date"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Appointment).options(
        selectinload(Appointment.doctor),
        selectinload(Appointment.patient),
    )
    if doctor_id is not None:
        stmt = stmt.where(Appointment.doctor_id == doctor_id)
    if patient_id is not None:
        stmt = stmt.where(Appointment.patient_id == patient_id)
    if on_date is not None:
        stmt = stmt.where(Appointment.appointment_date == on_date)
    stmt = stmt.order_by(Appointment.appointment_date, Appointment.start_time)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{appt_id}", response_model=AppointmentRead)
async def get_appointment(appt_id: int, db: AsyncSession = Depends(get_db)):
    appt = await db.get(Appointment, appt_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return appt


@router.post("/", response_model=AppointmentRead, status_code=201)
async def create_appointment(data: AppointmentCreate, db: AsyncSession = Depends(get_db)):
    if data.slot_id:
        slot = await db.get(ScheduleSlot, data.slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail="Слот не найден")

    # Check for any overlapping booked appointment (same doctor, date, time)
    existing = await db.execute(
        select(Appointment).where(
            Appointment.doctor_id == data.doctor_id,
            Appointment.appointment_date == data.appointment_date,
            Appointment.start_time == data.start_time,
            Appointment.status == AppointmentStatus.BOOKED,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Слот уже занят на это время")

    appt = Appointment(**data.model_dump(), status=AppointmentStatus.BOOKED)
    db.add(appt)
    await db.commit()
    await db.refresh(appt)
    return appt


@router.put("/{appt_id}/cancel", response_model=AppointmentRead)
async def cancel_appointment(appt_id: int, db: AsyncSession = Depends(get_db)):
    appt = await db.get(Appointment, appt_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    if appt.status != AppointmentStatus.BOOKED:
        raise HTTPException(status_code=400, detail="Можно отменить только активную запись")
    appt.status = AppointmentStatus.CANCELLED
    await db.commit()
    await db.refresh(appt)
    return appt


@router.put("/{appt_id}/complete", response_model=AppointmentRead)
async def complete_appointment(appt_id: int, db: AsyncSession = Depends(get_db)):
    appt = await db.get(Appointment, appt_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    appt.status = AppointmentStatus.COMPLETED
    await db.commit()
    await db.refresh(appt)
    return appt


@router.delete("/{appt_id}", status_code=204)
async def delete_appointment(appt_id: int, db: AsyncSession = Depends(get_db)):
    appt = await db.get(Appointment, appt_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    await db.delete(appt)
    await db.commit()
