import os
os.environ["DATABASE_URL"] = "sqlite:///./test_mediqueue.db"
os.environ["DEMO_SEED"] = "true"
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_departments_exist():
    response = client.get("/api/departments")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_booking_and_lookup():
    departments = client.get("/api/departments").json()
    dept = departments[0]
    doctors = client.get(f"/api/doctors?department_id={dept['id']}").json()
    assert doctors
    from datetime import date, timedelta
    payload = {"patient_name":"Pytest Demo", "patient_contact":"pytest@example.test",
               "department_id":dept["id"], "doctor_id":doctors[0]["id"],
               "appointment_date":str(date.today()+timedelta(days=3))}
    booked = client.post("/api/appointments", json=payload)
    assert booked.status_code == 201
    aid = booked.json()["id"]
    assert client.get(f"/api/appointments/{aid}").status_code == 200
