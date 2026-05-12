import requests


def get_check_suite_count(owner, repo, token, commit_sha):
    check_suite_url = f'https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}/check-suites'
    headers = {'Authorization': f'token {token}'}
    check_suite_response = requests.get(check_suite_url, headers=headers)
    if check_suite_response.status_code == 200:
        return check_suite_response.json()['total_count']
    else:
        print(
            f"Failed to retrieve check suites for commit {commit_sha}. Status code: {check_suite_response.status_code}")
        return None


def get_check_suite(owner, repo, token, commit_sha):
    check_suite_url = f'https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}/check-suites'
    headers = {'Authorization': f'token {token}'}
    check_suite_response = requests.get(check_suite_url, headers=headers)
    if check_suite_response.status_code == 200:
        return check_suite_response.json()
    else:
        print(
            f"Failed to retrieve check suites for commit {commit_sha}. Status code: {check_suite_response.status_code}")
        return None


def get_check_runs(owner, repo, token, check_suite_id):
    check_runs_url = f'https://api.github.com/repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs'
    headers = {'Authorization': f'token {token}'}
    check_runs_response = requests.get(check_runs_url, headers=headers)
    if check_runs_response.status_code == 200:
        return check_runs_response.json()['check_runs']
    else:
        print(
            f"Failed to retrieve check runs for check suite {check_suite_id}. Status code: {check_runs_response.status_code}")
        return None
