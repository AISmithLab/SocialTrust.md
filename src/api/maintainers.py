# /users/{user}/repos

import requests
from requests import RequestException


def get_repos_from_maintainer(owner, repo, token):
    repo_url = f"https://api.github.com/users/{owner}/repos"
    headers = {'Authorization': f'token {token}'}
    try:
        repo_response = requests.get(repo_url, headers=headers)
        return repo_response.json()
    except RequestException as e:
        print(f"An error occurred while fetching repos : {e}")
        return None


def get_all_repos_from_maintainer(owner, token):
    repo_url = f"https://api.github.com/users/{owner}/repos"
    headers = {'Authorization': f'token {token}'}
    repos = []
    page = 1
    per_page = 100
    while True:
        try:
            params = {'page': page, 'per_page': per_page}
            repo_response = requests.get(repo_url, params=params, headers=headers)
            if repo_response.status_code == 200:
                repos_data = repo_response.json()
                if not repos_data:
                    break
                repos.extend(repos_data)
                if len(repos) > 1000:
                    break
                page += 1
        except RequestException as e:
            print(f"An error occurred while fetching repos : {e}")
            return None
    return repos
