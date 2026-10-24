import os
from datetime import date, timedelta
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Department, Doctor, Appointment
from .schemas import BookingIn, StatusIn
from .seed import seed_database

app = FastAPI(title="MediQueue API", version="1.0.0",
              description="Educational OPD queue demo using synthetic data only.")
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    if os.getenv("DEMO_SEED", "true").lower() == "true":
        seed_database()

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/health")
def health():
    return {"status": "ok", "service": "mediqueue"}

@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(select(1))
        return {"status": "ready", "database": "reachable"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc

@app.get("/api/departments")
def departments(db: Session = Depends(get_db)):
    return [{"id": d.id, "name": d.name, "description": d.description}
            for d in db.scalars(select(Department).order_by(Department.name)).all()]

@app.get("/api/doctors")
def doctors(department_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Doctor).order_by(Doctor.name)
    if department_id is not None:
        query = query.where(Doctor.department_id == department_id)
    return [{"id": d.id, "name": d.name, "department_id": d.department_id,
             "slot_capacity": d.slot_capacity} for d in db.scalars(query).all()]

@app.post("/api/appointments", status_code=201)
def book(payload: BookingIn, db: Session = Depends(get_db)):
    if payload.appointment_date < date.today():
        raise HTTPException(status_code=422, detail="Appointment date cannot be in the past")
    department = db.get(Department, payload.department_id)
    doctor = db.get(Doctor, payload.doctor_id)
    if not department or not doctor or doctor.department_id != payload.department_id:
        raise HTTPException(status_code=400, detail="Choose a valid doctor for this department")
    count = db.scalar(select(func.count(Appointment.id)).where(
        Appointment.doctor_id == payload.doctor_id,
        Appointment.appointment_date == payload.appointment_date,
        Appointment.status != "cancelled"
    )) or 0
    if count >= doctor.slot_capacity:
        raise HTTPException(status_code=409, detail="No appointment slots remain for this doctor on that date")
    appointment = Appointment(**payload.model_dump(), token_number=count + 1, status="waiting")
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment_view(appointment, db)

def appointment_view(a, db):
    ahead = db.scalar(select(func.count(Appointment.id)).where(
        Appointment.doctor_id == a.doctor_id,
        Appointment.appointment_date == a.appointment_date,
        Appointment.token_number < a.token_number,
        Appointment.status == "waiting"
    )) or 0
    return {"id": a.id, "token_number": a.token_number, "patient_name": a.patient_name,
            "department_id": a.department_id, "doctor_id": a.doctor_id,
            "appointment_date": str(a.appointment_date), "status": a.status,
            "people_ahead": ahead, "estimated_wait_minutes": ahead * 8}

@app.get("/api/appointments/{appointment_id}")
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment_view(appointment, db)

@app.get("/api/queue")
def queue(department_id: int | None = None, appointment_date: date | None = None,
          db: Session = Depends(get_db)):
    target = appointment_date or date.today()
    query = select(Appointment).where(Appointment.appointment_date == target,
                                      Appointment.status.in_(["waiting", "in_consultation"]))
    if department_id is not None:
        query = query.where(Appointment.department_id == department_id)
    records = db.scalars(query.order_by(Appointment.token_number)).all()
    return [appointment_view(a, db) for a in records]

@app.get("/api/staff/summary")
def staff_summary(db: Session = Depends(get_db)):
    target = date.today() + timedelta(days=1)
    rows = db.execute(select(Appointment.status, func.count(Appointment.id))
                      .where(Appointment.appointment_date == target)
                      .group_by(Appointment.status)).all()
    counts = {status: count for status, count in rows}
    total = sum(counts.values())
    return {"date": str(target), "total_appointments": total,
            "waiting": counts.get("waiting", 0),
            "in_consultation": counts.get("in_consultation", 0),
            "completed": counts.get("completed", 0),
            "cancelled": counts.get("cancelled", 0),
            "synthetic_data": True}

@app.patch("/api/appointments/{appointment_id}/status")
def update_status(appointment_id: int, payload: StatusIn, db: Session = Depends(get_db)):
    allowed = {"waiting", "in_consultation", "completed", "cancelled"}
    if payload.status not in allowed:
        raise HTTPException(status_code=422, detail=f"status must be one of {sorted(allowed)}")
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment.status = payload.status
    db.commit()
    db.refresh(appointment)
    return appointment_view(appointment, db)
