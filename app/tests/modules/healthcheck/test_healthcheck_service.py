def test_healthcheck(anon_client):
    response = anon_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json().get("ok") is True
