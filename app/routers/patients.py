from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.database_models import Patient
from app.models.schemas import PatientCreate, PatientRead

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("/", response_model=list[PatientRead])
async def list_patients(
    search: str = Query("", description="Поиск по ФИО или телефону"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Patient).order_by(Patient.last_name)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            (Patient.last_name.ilike(pattern))
            | (Patient.first_name.ilike(pattern))
            | (Patient.phone.ilike(pattern))
        )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{patient_id}", response_model=PatientRead)
async def get_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return patient


@router.post("/", response_model=PatientRead, status_code=201)
async def create_patient(data: PatientCreate, db: AsyncSession = Depends(get_db)):
    patient = Patient(**data.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.put("/{patient_id}", response_model=PatientRead)
async def update_patient(patient_id: int, data: PatientCreate, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    for k, v in data.model_dump().items():
        setattr(patient, k, v)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=204)
async def delete_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    await db.delete(patient)
    await db.commit()
