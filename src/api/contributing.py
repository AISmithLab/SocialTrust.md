import base64

import requests
import time

def get_contributing(owner, repo, token):
    headers = {'Authorization': f'token {token}'}

    def fetch_contributing_file(file_name):
        while True:
            try:
                contributing_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_name}"
                contributing_response = requests.get(contributing_url, headers=headers)
                if contributing_response.status_code == 200:
                    return base64.b64decode(contributing_response.json()["content"]).decode("utf-8")
                elif contributing_response.status_code == 404:
                    print(f"{file_name} not found (404). Trying another file...")
                    return None
                else:
                    print(f"Failed to retrieve {file_name}. Status code: {contributing_response.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    result = fetch_contributing_file("CONTRIBUTING.md")
    if result is None:
        result = fetch_contributing_file("contributing.md")

    if result:
        return result
    else:
        return None
