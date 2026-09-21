from datetime import date, time
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ── Doctor ──────────────────────────────────────────────
class DoctorCreate(BaseModel):
    first_name: str
    last_name: str
    patronymic: str = ""
    specialty: str
    cabinet: str
    phone: str = ""
    email: str = ""


class DoctorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    patronymic: str
    specialty: str
    cabinet: str
    phone: str
    email: str
    full_name: str
    initials: str


# ── Patient ─────────────────────────────────────────────
class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    patronymic: str = ""
    phone: str
    email: str = ""
    date_of_birth: Optional[date] = None
    address: str = ""


class PatientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    patronymic: str
    phone: str
    email: str
    date_of_birth: Optional[date]
    address: str
    full_name: str


# ── Schedule Slot ───────────────────────────────────────
class SlotCreate(BaseModel):
    doctor_id: int
    day_of_week: int  # 0=Mon .. 6=Sun
    start_time: time
    end_time: time


class SlotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int
    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool


# ── Appointment ─────────────────────────────────────────
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    slot_id: Optional[int] = None
    appointment_date: date
    start_time: time
    end_time: time
    notes: str = ""


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    slot_id: Optional[int]
    appointment_date: date
    start_time: time
    end_time: time
    status: str
    notes: str
