import base64

import requests


def get_code_of_conduct(owner, repo, token):
    code_of_conduct_url = f"https://api.github.com/repos/{owner}/{repo}/contents/code-of-conduct.md"

    headers = {'Authorization': f'token {token}'}
    code_of_conduct_response = requests.get(code_of_conduct_url, headers=headers)
    if code_of_conduct_response.status_code == 200:
        return base64.b64decode(code_of_conduct_response.json()["content"]).decode("utf-8")

    code_of_conduct_url = f"https://api.github.com/repos/{owner}/{repo}/contents/code_of_conduct.md"

    headers = {'Authorization': f'token {token}'}
    code_of_conduct_response = requests.get(code_of_conduct_url, headers=headers)
    if code_of_conduct_response.status_code == 200:
        return base64.b64decode(code_of_conduct_response.json()["content"]).decode("utf-8")

    code_of_conduct_url = f"https://api.github.com/repos/{owner}/{repo}/contents/CODE-OF-CONDUCT.md"

    headers = {'Authorization': f'token {token}'}
    code_of_conduct_response = requests.get(code_of_conduct_url, headers=headers)
    if code_of_conduct_response.status_code == 200:
        return base64.b64decode(code_of_conduct_response.json()["content"]).decode("utf-8")

    print(f"Failed to retrieve code_of_conduct. Status code: {code_of_conduct_response.status_code}")
    return None
