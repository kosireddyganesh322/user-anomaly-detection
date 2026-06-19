import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "anomaly-detection-api"}

def test_dashboard_overview(client):
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "anomalies_detected" in data
    assert "high_risk_users" in data
    assert "critical_users" in data

def test_get_users(client):
    response = client.get("/api/users/?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert len(data["users"]) <= 5

def test_get_alerts(client):
    response = client.get("/api/alerts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        alert = data[0]
        assert "user_id" in alert
        assert "severity" in alert
        assert "acknowledged" in alert

def test_predictions_run_mocked(client, monkeypatch):
    # Mock heavy pipeline run functions to ensure fast unit tests execution
    import ml.risk_scoring.risk_engine
    import ml.prediction.predict
    import ml.prediction.generate_security_profile

    monkeypatch.setattr(ml.risk_scoring.risk_engine, "run_risk_scoring", lambda *a, **kw: None)
    monkeypatch.setattr(ml.prediction.predict, "predict", lambda *a, **kw: None)
    monkeypatch.setattr(ml.prediction.generate_security_profile, "generate_profile", lambda *a, **kw: None)

    response = client.post("/api/predictions/run")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_predictions_results(client):
    response = client.get("/api/predictions/results")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_advanced_soc_analytics_routes(client):
    # Test top risk users
    r = client.get("/api/analytics/top-risk-users")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    if r.json():
        assert "risk_score" in r.json()[0]
        assert "risk_level" in r.json()[0]
    
    # Test department risk ranking
    r = client.get("/api/analytics/department-risk-ranking")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    if r.json():
        assert "avg_risk_score" in r.json()[0]
        assert "suspicious_users" in r.json()[0]
        
    # Test anomaly reason breakdown
    r = client.get("/api/analytics/anomaly-reason-breakdown")
    assert r.status_code == 200
    assert "No Significant Anomalies" in r.json()
    
    # Test threat heatmap
    r = client.get("/api/analytics/threat-heatmap")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    if r.json():
        assert "Low" in r.json()[0]
        assert "Critical" in r.json()[0]
        
    # Test security posture score
    r = client.get("/api/analytics/security-posture")
    assert r.status_code == 200
    assert "score" in r.json()
    assert "status" in r.json()
    
    # Test risk matrix
    r = client.get("/api/analytics/risk-matrix")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    if r.json():
        assert "anomaly_score" in r.json()[0]
        assert "risk_score" in r.json()[0]
        
    # Test behavioral indicators
    r = client.get("/api/analytics/behavioral-indicators")
    assert r.status_code == 200
    assert "avg_usb_connections" in r.json()
    assert "avg_after_hours_ratio" in r.json()
    
    # Test watchlist
    r = client.get("/api/analytics/watchlist")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    if r.json():
        assert "security_status" in r.json()[0]


def test_acknowledge_alerts(client):
    # Get active alerts
    r = client.get("/api/alerts/?acknowledged=false")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    
    if data:
        alert_id = data[0]["id"]
        # Acknowledge single alert
        ack_res = client.put(f"/api/alerts/{alert_id}/acknowledge")
        assert ack_res.status_code == 200
        assert ack_res.json()["success"] is True
        assert ack_res.json()["alert_id"] == alert_id
        
        # Acknowledge all alerts
        ack_all_res = client.put("/api/alerts/acknowledge-all")
        assert ack_all_res.status_code == 200
        assert ack_all_res.json()["success"] is True
        assert "count" in ack_all_res.json()
        
        # Verify that active alerts are now 0
        r_after = client.get("/api/alerts/?acknowledged=false")
        assert r_after.status_code == 200
        assert len(r_after.json()) == 0


