from datetime import datetime

import pytest


RESOURCE_CASES = [
    (
        "academics",
        {
            "title": "Semester 6 Project Viva",
            "description": "Final project evaluation",
            "event_type": "examination",
            "course": "BSc IT",
            "semester": "6",
            "starts_at": datetime(2027, 4, 2, 10).isoformat(),
            "ends_at": None,
            "location": "Lab 3",
            "resource_url": None,
            "is_published": True,
        },
        {"title": "Updated Project Viva"},
        "title",
        "Updated Project Viva",
    ),
    (
        "knowledge",
        {
            "category": "VSIT",
            "topic": "library",
            "question": "When is the library open?",
            "answer": "The library is open during college hours.",
        },
        {"answer": "Please check the current library notice."},
        "answer",
        "Please check the current library notice.",
    ),
    (
        "faculty",
        {
            "name": "Prof. Sample Faculty",
            "department": "Information Technology",
            "designation": "Assistant Professor",
            "subjects": "Python, DBMS",
            "email": "faculty@example.edu",
            "phone": None,
            "office_hours": "Monday 2 PM",
            "office_location": "Faculty Room",
            "is_hod": False,
        },
        {"designation": "Associate Professor"},
        "designation",
        "Associate Professor",
    ),
    (
        "offices",
        {
            "office_name": "Student Section",
            "department": "Administration",
            "purpose": "Student documents",
            "timings": "10 AM to 4 PM",
            "location": "Ground Floor",
            "contact_person": "Office Assistant",
            "contact_email": "studentsection@example.edu",
            "contact_phone": None,
            "procedure_details": "Bring your ID card.",
            "is_active": True,
        },
        {"location": "First Floor"},
        "location",
        "First Floor",
    ),
]


def admin_headers(client):
    response = client.post(
        "/api/auth/login",
        json={"password": "test-admin-password"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("resource,payload,update,key,expected", RESOURCE_CASES)
def test_admin_resources_require_auth_and_support_crud(
    client,
    resource,
    payload,
    update,
    key,
    expected,
):
    endpoint = f"/api/admin/{resource}"
    assert client.post(endpoint, json=payload).status_code == 401

    headers = admin_headers(client)
    created = client.post(endpoint, json=payload, headers=headers)
    assert created.status_code == 201
    record_id = created.json()["id"]

    listed = client.get(endpoint, headers=headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [record_id]

    updated = client.patch(
        f"{endpoint}/{record_id}",
        json=update,
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()[key] == expected

    deleted = client.delete(f"{endpoint}/{record_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get(endpoint, headers=headers).json() == []


def test_deleting_unknown_admin_record_returns_404(client):
    response = client.delete(
        "/api/admin/faculty/99999",
        headers=admin_headers(client),
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "resource,payload",
    [
        ("academics", {"title": ""}),
        ("faculty", {"name": "", "department": "Information Technology"}),
        ("offices", {"office_name": ""}),
    ],
)
def test_admin_rejects_blank_required_names(client, resource, payload):
    response = client.post(
        f"/api/admin/{resource}",
        json=payload,
        headers=admin_headers(client),
    )

    assert response.status_code == 422
