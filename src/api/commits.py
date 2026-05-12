import time
import requests


def get_commit_by_sha(owner, repo, token, commit_sha):
    commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
    headers = {'Authorization': f'token {token}'}
    while True:
        try:
            commit_response = requests.get(commit_url, headers=headers)
            if commit_response.status_code == 200:
                return commit_response.json()
            else:
                print(f"Failed to retrieve commit. Status code: {commit_response.status_code}. Retrying in 5 seconds...")
                time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying in {5} seconds...")
            time.sleep(5)


def get_all_commits(owner, repo, token):
    url = f'https://api.github.com/repos/{owner}/{repo}/commits'
    commits = []
    headers = {'Authorization': f'token {token}'}
    page = 1
    per_page = 100
    while True:
        params = {'page': page, 'per_page': per_page}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            commits_data = response.json()
            if not commits_data:
                break
            commits.extend(commits_data)
            page += 1
        else:
            print(f"Failed to retrieve commits. Status code: {response.status_code}")
            return None
    return commits

def get_recent_commits(owner, repo, token):
    start_date = "2023-07-01T00:00:01Z"
    url = f'https://api.github.com/repos/{owner}/{repo}/commits?since={start_date}'
    commits = []
    headers = {'Authorization': f'token {token}'}
    page = 1
    per_page = 100
    while True:
        params = {'page': page, 'per_page': per_page}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            commits_data = response.json()
            if not commits_data:
                break
            commits.extend(commits_data)
            page += 1
        else:
            print(f"Failed to retrieve commits. Status code: {response.status_code}")
            return None
    return commits
