import urllib.request
import urllib.parse
import json
import time
import os

mock_dir = r"C:\Users\SHIVAGANESH REDDY\.gemini\antigravity-ide\brain\4b5e75b8-0bc7-44ea-b75c-95dc1b1f9386\scratch\mock_dataset"

# Prepare multipart/form-data boundary
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'

def build_multipart_form(fields, files):
    body = []
    for k, v in fields.items():
        body.append(f'--{boundary}')
        body.append(f'Content-Disposition: form-data; name="{k}"')
        body.append('')
        body.append(str(v))
        
    for k, filepath in files.items():
        filename = os.path.basename(filepath)
        body.append(f'--{boundary}')
        body.append(f'Content-Disposition: form-data; name="{k}"; filename="{filename}"')
        body.append('Content-Type: text/csv')
        body.append('')
        with open(filepath, 'rb') as f:
            body.append(f.read())
            
    body.append(f'--{boundary}--')
    body.append('')
    
    # We must join bytes, so convert strings to bytes
    binary_body = []
    for x in body:
        if isinstance(x, str):
            binary_body.append(x.encode('utf-8'))
        else:
            binary_body.append(x)
            
    return b'\r\n'.join(binary_body)

# Call API to upload
fields = {"name": "NFC_Test"}
files = {
    "users": os.path.join(mock_dir, "users.csv"),
    "logon": os.path.join(mock_dir, "logon.csv"),
    "device": os.path.join(mock_dir, "device.csv"),
    "ldap": os.path.join(mock_dir, "ldap.csv")
}

data_body = build_multipart_form(fields, files)

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/datasets/upload",
    data=data_body,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(data_body))
    }
)

print("Uploading files and starting background pipeline...")
try:
    response = urllib.request.urlopen(req)
    res_data = json.loads(response.read().decode())
    print("Upload response:", json.dumps(res_data, indent=2))
except Exception as e:
    print("Upload request failed:", e)
    if hasattr(e, 'read'):
        print("Response details:", e.read().decode())
    exit(1)

# Poll status
print("Polling status of reprocessing for 'NFC_Test'...")
for i in range(15):
    time.sleep(2)
    try:
        url = "http://127.0.0.1:8000/api/datasets/NFC_Test/status"
        response = urllib.request.urlopen(url)
        status_data = json.loads(response.read().decode())
        print(f"Poll {i+1}: Status={status_data['status']}, Progress={status_data['progress']}% (Current Step: {status_data['current_step']})")
        if status_data['status'] == 'Success':
            print("Pipeline processing completed successfully!")
            break
        elif status_data['status'] == 'Failed':
            print("Pipeline failed:", status_data.get('error'))
            exit(1)
    except Exception as e:
        print("Failed to fetch status:", e)

# Switch dataset
print("Switching active dataset to 'NFC_Test'...")
try:
    req_switch = urllib.request.Request(
        "http://127.0.0.1:8000/api/datasets/switch",
        data=json.dumps({"name": "NFC_Test"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    response = urllib.request.urlopen(req_switch)
    switch_res = json.loads(response.read().decode())
    print("Switch response:", switch_res)
except Exception as e:
    print("Switch failed:", e)
    exit(1)

# Check active metadata
print("Verifying active dataset metadata...")
try:
    url = "http://127.0.0.1:8000/api/datasets/active"
    response = urllib.request.urlopen(url)
    active_meta = json.loads(response.read().decode())
    print("Active Metadata:")
    print(json.dumps(active_meta, indent=2))
except Exception as e:
    print("Failed to get active metadata:", e)

# Verify overview
print("Verifying active dashboard overview metrics...")
try:
    url = "http://127.0.0.1:8000/api/dashboard/overview"
    response = urllib.request.urlopen(url)
    overview = json.loads(response.read().decode())
    print("Overview Metrics:")
    print(json.dumps(overview, indent=2))
except Exception as e:
    print("Failed to get overview:", e)

# Switch back to CERT
print("Switching active dataset back to 'CERT'...")
try:
    req_switch = urllib.request.Request(
        "http://127.0.0.1:8000/api/datasets/switch",
        data=json.dumps({"name": "CERT"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    response = urllib.request.urlopen(req_switch)
    print("Switched back successfully.")
except Exception as e:
    print("Switch back failed:", e)
