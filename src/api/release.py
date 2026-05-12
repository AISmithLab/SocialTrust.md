import requests
from requests import RequestException


def get_releases(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {'Authorization': f'token {token}'}
    releases = []
    page = 1
    per_page = 100
    while True:
        try:
            params = {'page': page, 'per_page': per_page}
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                releases_data = response.json()
                if not releases_data:
                    break
                releases.extend(releases_data)
                page += 1
        except RequestException as e:
            print(f"An error occurred : {e}. Skipping this issue.")
            return None
    return releases
