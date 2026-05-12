import requests
from bs4 import BeautifulSoup
from requests import RequestException


def get_recent_pull_requests(owner, repo, token, params=None):
    start_date = "2023-07-01T00:00:01Z"
    pulls_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&since={start_date}"
    headers = {'Authorization': f'token {token}'}
    pulls = []
    page = 1
    while True:
        paged_params = params.copy() if params else {}
        paged_params.update({'page': page, 'per_page': 100})
        try:
            pulls_response = requests.get(pulls_url, params=paged_params, headers=headers)
            pulls_response.raise_for_status()
            pulls_data = pulls_response.json()
            if not pulls_data:
                break
            for pull in pulls_data:
                if 'pull' in pull.get('html_url', ''):
                    pulls.append(pull)
            if len(pulls_data) > 1000:
                break
            page += 1
        except RequestException as e:
            print(f"An error occurred while fetching pulls : {e}")
            raise
    return pulls


def get_pull_requests_by_state(owner, repo, token, state=None):
    pull_requests_url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state={state}"
    headers = {'Authorization': f'token {token}'}
    pull_requests = []
    page = 1
    per_page = 100
    while True:
        params = {'page': page, 'per_page': per_page}
        pulls_request_response = requests.get(pull_requests_url, params=params, headers=headers)
        if pulls_request_response.status_code == 200:
            pull_requests_data = pulls_request_response.json()
            if not pull_requests_data:
                break
            pull_requests.extend(pull_requests_data)
            page += 1
        else:
            print(f"Failed to retrieve pull requests. Status code: {pulls_request_response.status_code}")
            return None
    return pull_requests


def get_recent_n_pull_requests(owner, repo, token, n):
    pull_requests_url = f'https://api.github.com/repos/{owner}/{repo}/pulls?state=all'
    params = {'per_page': f'{n}'}
    headers = {'Authorization': f'Token {token}'}
    pulls_request_response = requests.get(pull_requests_url, params=params, headers=headers)
    if pulls_request_response.status_code == 200:
        return pulls_request_response.json()
    else:
        print(f"Failed to retrieve pull requests. Status code: {pulls_request_response.status_code}")
        return None


def get_pulls_rate(owner, repo):
    url = f"https://github.com/{owner}/{repo}/pulls"
    print("GET " + url)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "html.parser")
            open_pulls = soup.find_all('a', {'data-ga-click': "Pull Requests, Table state, Open"})
            closed_pulls = soup.find_all('a', {'data-ga-click': "Pull Requests, Table state, Closed"})
            if open_pulls and closed_pulls:
                data = {
                    'open_pulls': int(open_pulls[0].text.strip().split(" ")[0].replace(',', '')),
                    'closed_pulls': int(closed_pulls[0].text.strip().split(" ")[0].replace(',', ''))
                }
                return data
    except RequestException as e:
        print(f"An error occurred while fetching: {e}. Skipping this pull.")
        return None
