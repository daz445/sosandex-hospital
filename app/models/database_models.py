import enum
from datetime import date, time
from sqlalchemy import (
    Column, Integer, String, Date, Time, Enum, ForeignKey, Text, Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base


class AppointmentStatus(str, enum.Enum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    patronymic = Column(String(100), default="")
    specialty = Column(String(150), nullable=False)
    cabinet = Column(String(20), nullable=False)
    phone = Column(String(20), default="")
    email = Column(String(150), default="")

    appointments = relationship("Appointment", back_populates="doctor")
    schedule_slots = relationship("ScheduleSlot", back_populates="doctor")

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.patronymic:
            parts.append(self.patronymic)
        return " ".join(parts)

    @property
    def initials(self):
        i = self.first_name[0] if self.first_name else ""
        l = self.last_name[0] if self.last_name else ""
        return f"{l}{i}"


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    patronymic = Column(String(100), default="")
    phone = Column(String(20), nullable=False)
    email = Column(String(150), default="")
    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, default="")

    appointments = relationship("Appointment", back_populates="patient")

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name]
        if self.patronymic:
            parts.append(self.patronymic)
        return " ".join(parts)


class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday .. 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)

    doctor = relationship("Doctor", back_populates="schedule_slots")
    appointments = relationship("Appointment", back_populates="slot")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("schedule_slots.id"), nullable=True)
    appointment_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.BOOKED)
    notes = Column(Text, default="")

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    slot = relationship("ScheduleSlot", back_populates="appointments")
