from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(250), default="")
    doctors: Mapped[list["Doctor"]] = relationship(back_populates="department")

class Doctor(Base):
    __tablename__ = "doctors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    slot_capacity: Mapped[int] = mapped_column(Integer, default=30)
    department: Mapped[Department] = relationship(back_populates="doctors")

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True)
    token_number: Mapped[int] = mapped_column(Integer, nullable=False)
    patient_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patient_contact: Mapped[str] = mapped_column(String(160), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    appointment_date: Mapped[object] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="waiting", nullable=False)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
