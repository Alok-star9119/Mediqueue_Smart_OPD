"""Seed the database with fictional demo data. No real patient data is used."""
from datetime import date, timedelta
from sqlalchemy import select
from .database import Base, engine, SessionLocal
from .models import Department, Doctor, Appointment

DEPARTMENTS = [
    ("General Medicine", "Routine consultations and primary care"),
    ("Pediatrics", "Child health consultations"),
    ("Dermatology", "Skin, hair and nail consultations"),
    ("Orthopedics", "Bone, joint and mobility consultations"),
]
DOCTORS = [
    ("Dr. Asha Demo", 0), ("Dr. Kabir Sample", 0),
    ("Dr. Mira Example", 1), ("Dr. Neel Fiction", 1),
    ("Dr. Tara Sample", 2), ("Dr. Om Demo", 3),
]
FAKE_NAMES = ["Aarav Example", "Diya Sample", "Kabir Demo", "Mira Fiction", "Ira Example",
              "Vivaan Sample", "Anaya Demo", "Reyansh Fiction", "Sara Example", "Arjun Sample"]

def seed_database():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(Department.id).limit(1)) is not None:
            return
        departments = [Department(name=n, description=d) for n, d in DEPARTMENTS]
        db.add_all(departments)
        db.flush()
        doctors = [Doctor(name=n, department_id=departments[idx].id, slot_capacity=30) for n, idx in DOCTORS]
        db.add_all(doctors)
        db.flush()
        target_date = date.today() + timedelta(days=1)
        counts = {}
        for i, name in enumerate(FAKE_NAMES):
            dept = departments[i % len(departments)]
            doctor = next(d for d in doctors if d.department_id == dept.id)
            counts[doctor.id] = counts.get(doctor.id, 0) + 1
            db.add(Appointment(
                token_number=counts[doctor.id], patient_name=name,
                patient_contact=f"patient{i+1}@example.test", department_id=dept.id,
                doctor_id=doctor.id, appointment_date=target_date,
                status="waiting" if i % 4 else "completed"
            ))
        db.commit()

if __name__ == "__main__":
    seed_database()
