import os
import requests
from dotenv import load_dotenv

# 1. Load the secrets
load_dotenv()

host = os.getenv("DATABRICKS_HOST")
token = os.getenv("DATABRICKS_TOKEN")

# 2. Package the token securely into the request headers
# The API requires the token to be sent as a "Bearer" token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 3. Define the specific API endpoint we want to talk to
# We are asking the Jobs API to list the jobs in your workspace
url = f"{host}/api/2.1/jobs/list"

print(f"Attempting to connect to Databricks at: {host}...")

# 4. Make the call and capture the response
response = requests.get(url, headers=headers)

# 5. Check if it worked
if response.status_code == 200:
    print("\n✅ SUCCESS! Connection established.")
    data = response.json()
    jobs = data.get("jobs", [])
    print(f"Found {len(jobs)} jobs in your workspace.")
else:
    print(f"\n❌ FAILED! Status Code: {response.status_code}")
    print(f"Error Message: {response.text}")