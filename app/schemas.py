from datetime import date
from pydantic import BaseModel, Field, ConfigDict

class BookingIn(BaseModel):
    patient_name: str = Field(min_length=2, max_length=100)
    patient_contact: str = Field(min_length=3, max_length=160)
    department_id: int = Field(gt=0)
    doctor_id: int = Field(gt=0)
    appointment_date: date

class StatusIn(BaseModel):
    status: str

class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    token_number: int
    patient_name: str
    department_id: int
    doctor_id: int
    appointment_date: date
    status: str
