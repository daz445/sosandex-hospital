import pytest


@pytest.mark.asyncio
async def test_create_patient(client):
    resp = await client.post("/api/patients/", json={
        "last_name": "Пациент",
        "first_name": "Новый",
        "patronymic": "Тестович",
        "phone": "+79001112233",
        "date_of_birth": "1990-05-15",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["last_name"] == "Пациент"
    assert data["full_name"] == "Пациент Новый Тестович"


@pytest.mark.asyncio
async def test_list_patients(client):
    await client.post("/api/patients/", json={
        "last_name": "Поиск", "first_name": "Тест",
        "phone": "+79002223344", "date_of_birth": "1985-01-01",
    })
    resp = await client.get("/api/patients/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_search_patients(client):
    await client.post("/api/patients/", json={
        "last_name": "УникальныйИванов", "first_name": "Сергей",
        "phone": "+79001234599", "date_of_birth": "1990-01-01",
    })
    resp = await client.get("/api/patients/", params={"search": "УникальныйИванов"})
    assert resp.status_code == 200
    assert any("УникальныйИванов" in p["last_name"] for p in resp.json())


@pytest.mark.asyncio
async def test_get_patient_404(client):
    resp = await client.get("/api/patients/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_patient(client):
    r = await client.post("/api/patients/", json={
        "last_name": "Удаляемый", "first_name": "Пациент",
        "phone": "0", "date_of_birth": "2000-01-01",
    })
    pid = r.json()["id"]
    resp = await client.delete(f"/api/patients/{pid}")
    assert resp.status_code == 204
