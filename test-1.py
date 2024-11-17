import pytest
from unittest.mock import patch
from datetime import datetime
from app import app, Students

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_students(client):
    mock_students = [
        Students(
            id=1,
            student_number="20231234",
            first_name="John",
            middle_name="A.",
            last_name="Doe",
            gender=1,
            birthday=datetime(2000, 1, 15),
        ),
        Students(
            id=2,
            student_number="20234567",
            first_name="Jane",
            middle_name="B.",
            last_name="Smith",
            gender=2,
            birthday=datetime(1999, 2, 20),
        ),
    ]

    with app.app_context():
        with patch("app.Students.query.all") as mock_all:
            mock_all.return_value = mock_students
            response = client.get("/students")
            assert response.status_code == 200
            json_data = response.get_json()
            assert json_data["success"] is True
            assert len(json_data["data"]) == 100

def test_get_student(client):
    mock_student = Students(
        id=1,
        student_number="20231234",
        first_name="John",
        middle_name="A.",
        last_name="Doe",
        gender=1,
        birthday=datetime(2000, 1, 15),
    )

    with app.app_context():
        with patch("app.Students.query.get") as mock_get:
            mock_get.return_value = mock_student
            response = client.get("/students/1")
            assert response.status_code == 200
            json_data = response.get_json()
            assert json_data["success"] is True
            assert json_data["data"]["id"] == 1

def test_update_student(client):
    existing_student = Students(
        id=1,
        student_number="20231234",
        first_name="John",
        middle_name="A.",
        last_name="Doe",
        gender=1,
        birthday=datetime(2000, 1, 15),
    )

    with app.app_context():
        with patch("app.Students.query.get") as mock_get, patch("app.db.session.commit", autospec=True):
            mock_get.return_value = existing_student
            updated_data = {
                "first_name": "Updated John",
                "last_name": "Updated Doe",
            }
            response = client.put("/students/1", json=updated_data)
            assert response.status_code == 200
            json_data = response.get_json()
            assert json_data["success"] is True
            assert json_data["data"]["first_name"] == "Updated John"
            
def test_delete_student(client):
    with app.app_context():
        with patch("app.Students.query.get") as mock_get, patch("app.db.session.delete"), patch("app.db.session.commit"):
            mock_student = Students(
                id=1,
                student_number="20231234",
                first_name="John",
                middle_name="A.",
                last_name="Doe",
                gender=1,
                birthday=datetime(2000, 1, 15),
            )
            mock_get.return_value = mock_student
            response = client.delete("/students/1")
            assert response.status_code == 204
            assert response.data == b''
