from fastapi.testclient import TestClient
from main import app
import os
import time

client = TestClient(app)

def test_upload_csv():
    with open("test.csv", "rb") as f:
        response = client.post("/files", files={"file": ("test.csv", f, "text/csv")})
    assert response.status_code == 200
    assert "file_id" in response.json()

def test_upload_excel():
    with open("test.xlsx", "rb") as f:
        response = client.post("/files", files={"file": ("test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert response.status_code == 200
    assert "file_id" in response.json()

def test_get_progress():
    with open("test.csv", "rb") as f:
        response = client.post("/files", files={"file": ("test.csv", f, "text/csv")})
    file_id = response.json()["file_id"]
    response = client.get(f"/files/{file_id}/progress")
    assert response.status_code == 200
    assert "status" in response.json()

def test_get_content():
    with open("test.xlsx", "rb") as f:
        response = client.post("/files", files={"file": ("test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    file_id = response.json()["file_id"]
    time.sleep(12)  # Wait for parsing to complete
    response = client.get(f"/files/{file_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_files():
    response = client.get("/files")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_file():
    with open("test.csv", "rb") as f:
        response = client.post("/files", files={"file": ("test.csv", f, "text/csv")})
    file_id = response.json()["file_id"]
    response = client.delete(f"/files/{file_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "File deleted"}