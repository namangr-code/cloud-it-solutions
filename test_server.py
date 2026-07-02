import urllib.request
import json
import subprocess
import time
import sys

# Start the server as a background process
print("Starting server.py in background...")
server_process = subprocess.Popen([sys.executable, "server.py"])
time.sleep(2) # Wait for server to boot

success = True

try:
    # Test Home Page
    print("Testing GET / ...")
    response = urllib.request.urlopen("http://localhost:3000/")
    html = response.read().decode('utf-8')
    if "CloudIT" in html:
        print("[OK] Home page loaded successfully!")
    else:
        print("[FAIL] Home page content match failed.")
        success = False

    # Test Assessments Endpoint GET
    print("Testing GET /api/assessments ...")
    response = urllib.request.urlopen("http://localhost:3000/api/assessments")
    data = json.loads(response.read().decode('utf-8'))
    if isinstance(data, list):
        print("[OK] GET /api/assessments loaded successfully!")
    else:
        print("[FAIL] GET /api/assessments returned incorrect format.")
        success = False

    # Test Assessments Endpoint POST
    print("Testing POST /api/assessments ...")
    payload = {
        "businessName": "Test Business",
        "industry": "retail",
        "size": "small",
        "budget": "medium",
        "securityImportance": "critical",
        "techExpertise": "low",
        "currentTools": ["excel", "paper"],
        "painPoints": ["collaboration", "accounting"]
    }
    
    req = urllib.request.Request(
        "http://localhost:3000/api/assessments",
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode('utf-8'))
    
    if result.get("id") and "recommendations" in result:
        print(f"[OK] POST /api/assessments created assessment {result['id']} successfully!")
    else:
        print("[FAIL] POST /api/assessments failed to create assessment.")
        success = False

except Exception as e:
    print(f"[FAIL] Network or validation error: {str(e)}")
    success = False

finally:
    # Kill the server
    print("Terminating server...")
    server_process.terminate()
    server_process.wait()

if success:
    print("\nAll server tests PASSED!")
    sys.exit(0)
else:
    print("\nSome server tests FAILED!")
    sys.exit(1)
