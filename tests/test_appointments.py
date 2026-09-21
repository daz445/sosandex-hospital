import pytest


async def _seed(client):
    """Create a doctor + patient and return their IDs."""
    d = await client.post("/api/doctors/", json={
        "last_name": "Док", "first_name": "Тест",
        "specialty": "Терапевт", "cabinet": "1", "phone": "0",
    })
    p = await client.post("/api/patients/", json={
        "last_name": "Пац", "first_name": "Тест",
        "phone": "0", "date_of_birth": "1990-01-01",
    })
    return d.json()["id"], p.json()["id"]


@pytest.mark.asyncio
async def test_create_appointment(client):
    doc_id, pat_id = await _seed(client)
    resp = await client.post("/api/appointments/", json={
        "doctor_id": doc_id, "patient_id": pat_id,
        "appointment_date": "2026-10-01",
        "start_time": "09:00:00", "end_time": "09:30:00",
    })
    assert resp.status_code == 201
    assert resp.json()["status"] == "booked"


@pytest.mark.asyncio
async def test_list_appointments(client):
    doc_id, pat_id = await _seed(client)
    await client.post("/api/appointments/", json={
        "doctor_id": doc_id, "patient_id": pat_id,
        "appointment_date": "2026-10-01",
        "start_time": "10:00:00", "end_time": "10:30:00",
    })
    resp = await client.get("/api/appointments/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_cancel_appointment(client):
    doc_id, pat_id = await _seed(client)
    r = await client.post("/api/appointments/", json={
        "doctor_id": doc_id, "patient_id": pat_id,
        "appointment_date": "2026-10-02",
        "start_time": "11:00:00", "end_time": "11:30:00",
    })
    appt_id = r.json()["id"]
    resp = await client.put(f"/api/appointments/{appt_id}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_complete_appointment(client):
    doc_id, pat_id = await _seed(client)
    r = await client.post("/api/appointments/", json={
        "doctor_id": doc_id, "patient_id": pat_id,
        "appointment_date": "2026-10-03",
        "start_time": "14:00:00", "end_time": "14:30:00",
    })
    appt_id = r.json()["id"]
    resp = await client.put(f"/api/appointments/{appt_id}/complete")
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_double_booking_conflict(client):
    doc_id, pat_id = await _seed(client)
    payload = {
        "doctor_id": doc_id, "patient_id": pat_id,
        "appointment_date": "2026-10-04",
        "start_time": "09:00:00", "end_time": "09:30:00",
    }
    r1 = await client.post("/api/appointments/", json=payload)
    assert r1.status_code == 201
    r2 = await client.post("/api/appointments/", json=payload)
    assert r2.status_code == 409
