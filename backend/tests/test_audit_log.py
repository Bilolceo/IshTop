def test_list_audit_logs_empty(client, super_admin_token):
    response = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {super_admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "logs" in data
    assert "total" in data
    assert isinstance(data["logs"], list)
