import urllib.request
import urllib.parse
import json
import os
import tempfile

mock_dir = r"C:\Users\SHIVAGANESH REDDY\.gemini\antigravity-ide\brain\4b5e75b8-0bc7-44ea-b75c-95dc1b1f9386\scratch\mock_dataset"
boundary = '----WebKitFormBoundaryValidationTest'

def build_multipart_form(files):
    body = []
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
    
    binary_body = []
    for x in body:
        if isinstance(x, str):
            binary_body.append(x.encode('utf-8'))
        else:
            binary_body.append(x)
            
    return b'\r\n'.join(binary_body)

# 1. Create a users.csv with missing column "department"
temp_dir = tempfile.mkdtemp()
bad_users_path = os.path.join(temp_dir, "users.csv")
with open(bad_users_path, "w") as f:
    f.write("user_id,name,role\n") # Missing "department"
    f.write("USR101,John Doe,Engineer\n")

# Use correct ones for the rest
files = {
    "users": bad_users_path,
    "logon": os.path.join(mock_dir, "logon.csv"),
    "device": os.path.join(mock_dir, "device.csv"),
    "ldap": os.path.join(mock_dir, "ldap.csv")
}

data_body = build_multipart_form(files)

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/datasets/validate",
    data=data_body,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(data_body))
    }
)

print("Calling pre-validation API with missing 'department' column in users.csv...")
try:
    response = urllib.request.urlopen(req)
    res_data = json.loads(response.read().decode())
    print("Validation Response:", json.dumps(res_data, indent=2))
    assert res_data["valid"] is False, "Expected valid to be False"
    assert "users.csv" in res_data["errors"]["missing_columns"], "Expected users.csv in error report"
    assert "department" in res_data["errors"]["missing_columns"]["users.csv"], "Expected department to be marked missing"
    print("Pre-validation failure detection test: SUCCESS!")
except Exception as e:
    print("Validation test failed:", e)
    if hasattr(e, 'read'):
        print("Details:", e.read().decode())
    exit(1)
finally:
    # Cleanup
    if os.path.exists(bad_users_path):
        os.remove(bad_users_path)
    os.rmdir(temp_dir)
