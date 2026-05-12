import base64

import requests
import time

def get_governance(owner, repo, token):
    headers = {'Authorization': f'token {token}'}

    def fetch_governance_file(file_name):
        while True:
            try:
                governance_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_name}"
                governance_response = requests.get(governance_url, headers=headers)
                if governance_response.status_code == 200:
                    return base64.b64decode(governance_response.json()["content"]).decode("utf-8")
                elif governance_response.status_code == 404:
                    print(f"{file_name} not found (404). Trying another file...")
                    return None
                else:
                    print(f"Failed to retrieve {file_name}. Status code: {governance_response.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    result = fetch_governance_file("GOVERNANCE.md")
    if result is None:
        result = fetch_governance_file("governance.md")
    if result:
        return result
    else:
        return None
