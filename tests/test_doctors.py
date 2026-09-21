import pytest


@pytest.mark.asyncio
async def test_create_doctor(client):
    resp = await client.post("/api/doctors/", json={
        "last_name": "Иванов",
        "first_name": "Петр",
        "patronymic": "Сергеевич",
        "specialty": "Терапевт",
        "cabinet": "101",
        "phone": "+79001234567",
        "email": "ivanov@hospital.ru",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["last_name"] == "Иванов"
    assert data["full_name"] == "Иванов Петр Сергеевич"


@pytest.mark.asyncio
async def test_list_doctors(client):
    await client.post("/api/doctors/", json={
        "last_name": "Петров", "first_name": "Сидор",
        "specialty": "Хирург", "cabinet": "202", "phone": "+79009990000",
    })
    resp = await client.get("/api/doctors/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_get_doctor_404(client):
    resp = await client.get("/api/doctors/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_doctor(client):
    r = await client.post("/api/doctors/", json={
        "last_name": "Сидоров", "first_name": "Антон",
        "specialty": "Офтальмолог", "cabinet": "303", "phone": "+79005551111",
    })
    doc_id = r.json()["id"]
    resp = await client.put(f"/api/doctors/{doc_id}", json={
        "last_name": "Сидоров", "first_name": "Антон",
        "specialty": "Невролог", "cabinet": "305", "phone": "+79005551111",
    })
    assert resp.status_code == 200
    assert resp.json()["specialty"] == "Невролог"


@pytest.mark.asyncio
async def test_delete_doctor(client):
    r = await client.post("/api/doctors/", json={
        "last_name": "Удаляемый", "first_name": "Доктор",
        "specialty": "Тест", "cabinet": "0", "phone": "0",
    })
    doc_id = r.json()["id"]
    resp = await client.delete(f"/api/doctors/{doc_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_create_doctor_slot(client):
    r = await client.post("/api/doctors/", json={
        "last_name": "Врач", "first_name": "Слот",
        "specialty": "Лор", "cabinet": "5", "phone": "0",
    })
    doc_id = r.json()["id"]
    resp = await client.post(f"/api/doctors/{doc_id}/slots", json={
        "doctor_id": doc_id, "day_of_week": 0,
        "start_time": "09:00:00", "end_time": "12:00:00",
    })
    assert resp.status_code == 201
    assert resp.json()["day_of_week"] == 0
