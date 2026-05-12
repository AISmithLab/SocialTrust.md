import time

import requests
from requests import RequestException


def get_workflow(owner, repo, token):
    workflow_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    headers = {'Authorization': f'token {token}'}
    try:
        workflow_response = requests.get(workflow_url, headers=headers)
        return workflow_response.json()
    except RequestException as e:
        print(f"An error occurred while fetching workflow : {e}")
        return None
