import requests


def get_all_branches(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        branches = [branch["name"] for branch in response.json()]
        return branches
    else:
        print(f"Failed to fetch branches, Status code: {response.status_code}")
        return None
