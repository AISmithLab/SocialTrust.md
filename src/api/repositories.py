import requests


def get_repo_info(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get repository info. Status code: {response.status_code}")
        return None


def get_repo_contents(owner, repo, token):
    base_url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get contents list. Status code: {response.status_code}")
        return None
