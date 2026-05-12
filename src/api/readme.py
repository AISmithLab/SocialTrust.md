import base64

import requests


def get_readme(owner, repo, token):
    readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    headers = {'Authorization': f'token {token}'}
    readme_response = requests.get(readme_url, headers=headers)
    if readme_response.status_code == 200:
        return base64.b64decode(readme_response.json()["content"]).decode("utf-8")
    else:
        print(f"Failed to retrieve dependents. Status code: {readme_response.status_code}")
        return None
