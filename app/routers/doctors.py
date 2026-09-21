from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.database_models import Doctor, ScheduleSlot
from app.models.schemas import DoctorCreate, DoctorRead, SlotCreate, SlotRead

router = APIRouter(prefix="/api/doctors", tags=["doctors"])


@router.get("/", response_model=list[DoctorRead])
async def list_doctors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Doctor).order_by(Doctor.last_name))
    return result.scalars().all()


@router.get("/{doctor_id}", response_model=DoctorRead)
async def get_doctor(doctor_id: int, db: AsyncSession = Depends(get_db)):
    doctor = await db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Врач не найден")
    return doctor


@router.post("/", response_model=DoctorRead, status_code=201)
async def create_doctor(data: DoctorCreate, db: AsyncSession = Depends(get_db)):
    doctor = Doctor(**data.model_dump())
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return doctor


@router.put("/{doctor_id}", response_model=DoctorRead)
async def update_doctor(doctor_id: int, data: DoctorCreate, db: AsyncSession = Depends(get_db)):
    doctor = await db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Врач не найден")
    for k, v in data.model_dump().items():
        setattr(doctor, k, v)
    await db.commit()
    await db.refresh(doctor)
    return doctor


@router.delete("/{doctor_id}", status_code=204)
async def delete_doctor(doctor_id: int, db: AsyncSession = Depends(get_db)):
    doctor = await db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Врач не найден")
    await db.delete(doctor)
    await db.commit()


# ── Schedule Slots ──────────────────────────────────────
@router.get("/{doctor_id}/slots", response_model=list[SlotRead])
async def list_doctor_slots(doctor_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ScheduleSlot)
        .where(ScheduleSlot.doctor_id == doctor_id)
        .order_by(ScheduleSlot.day_of_week, ScheduleSlot.start_time)
    )
    return result.scalars().all()


@router.post("/{doctor_id}/slots", response_model=SlotRead, status_code=201)
async def create_doctor_slot(doctor_id: int, data: SlotCreate, db: AsyncSession = Depends(get_db)):
    doctor = await db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Врач не найден")
    slot = ScheduleSlot(**data.model_dump())
    db.add(slot)
    await db.commit()
    await db.refresh(slot)
    return slot


@router.delete("/{doctor_id}/slots/{slot_id}", status_code=204)
async def delete_doctor_slot(doctor_id: int, slot_id: int, db: AsyncSession = Depends(get_db)):
    slot = await db.get(ScheduleSlot, slot_id)
    if not slot or slot.doctor_id != doctor_id:
        raise HTTPException(status_code=404, detail="Слот не найден")
    await db.delete(slot)
    await db.commit()
