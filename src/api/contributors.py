import requests


def get_all_contributors(owner, repo, token):
    headers = {'Authorization': f'token {token}'}
    contributors = []
    page = 1
    per_page = 100
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/contributors?page={page}&per_page={per_page}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            contributors.extend(response.json())
            if len(response.json()) < per_page:
                break
            else:
                page += 1
        else:
            print("Failed to fetch contributors")
            break
    return contributors
