import urllib.request
import json
import urllib.error

def fetch_json(url, data_payload=None, method='GET'):
    req = urllib.request.Request(url, method=method)
    if data_payload is not None:
        req.data = json.dumps(data_payload).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTPError on {url}: {e.code} - {e.read().decode('utf-8')}")
        raise e
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        raise e

# 1. Switch dataset to NFC_Test
print("Switching dataset to NFC_Test...")
switch_res = fetch_json("http://127.0.0.1:8000/api/datasets/switch", {"name": "NFC_Test"}, method='POST')
print("Switch Response:", switch_res)

endpoints = [
    ("Dashboard Overview", "http://127.0.0.1:8000/api/users/dashboard/overview"),
    ("Users List", "http://127.0.0.1:8000/api/users/"),
    ("Alerts List", "http://127.0.0.1:8000/api/alerts/"),
    ("Risk Distribution", "http://127.0.0.1:8000/api/analytics/risk-distribution"),
    ("Login Trends", "http://127.0.0.1:8000/api/analytics/login-trends"),
    ("Device Trends", "http://127.0.0.1:8000/api/analytics/device-trends"),
    ("Department Summary", "http://127.0.0.1:8000/api/analytics/department-summary"),
    ("Top Risk Users", "http://127.0.0.1:8000/api/analytics/top-risk-users"),
    ("Department Risk Ranking", "http://127.0.0.1:8000/api/analytics/department-risk-ranking"),
    ("Anomaly Reason Breakdown", "http://127.0.0.1:8000/api/analytics/anomaly-reason-breakdown"),
    ("Threat Heatmap", "http://127.0.0.1:8000/api/analytics/threat-heatmap"),
    ("Security Posture Score", "http://127.0.0.1:8000/api/analytics/security-posture"),
    ("Risk Matrix", "http://127.0.0.1:8000/api/analytics/risk-matrix"),
    ("Behavioral Indicators", "http://127.0.0.1:8000/api/analytics/behavioral-indicators"),
    ("Watchlist", "http://127.0.0.1:8000/api/analytics/watchlist")
]

all_passed = True
for name, url in endpoints:
    print(f"\n--- Testing Endpoint: {name} ({url}) ---")
    try:
        res = fetch_json(url)
        print("Success! Sample data:", json.dumps(res, indent=2)[:300] + ("..." if len(json.dumps(res)) > 300 else ""))
    except Exception as e:
        print(f"FAILED: {name}")
        all_passed = False

# Test export CSV report
print("\n--- Testing CSV Report Export ---")
try:
    csv_req = urllib.request.Request("http://127.0.0.1:8000/api/reports/export/csv?type=profile")
    csv_res = urllib.request.urlopen(csv_req)
    csv_data = csv_res.read().decode('utf-8')
    print(f"Success! CSV Head:\n{csv_data[:200]}...")
except Exception as e:
    print("FAILED: CSV Report Export", e)
    all_passed = False

# Switch back to CERT
print("\nSwitching back to CERT...")
switch_back = fetch_json("http://127.0.0.1:8000/api/datasets/switch", {"name": "CERT"}, method='POST')
print("Switch Back Response:", switch_back)

if all_passed:
    print("\nALL ENDPOINTS VERIFIED SUCCESSFULLY FOR CUSTOM DATASET!")
else:
    print("\nSOME ENDPOINTS FAILED TO LOAD TELEMETRY DATA!")
    exit(1)
