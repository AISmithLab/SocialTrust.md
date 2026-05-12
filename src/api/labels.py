# /repos/{owner}/{repo}/labels

import requests
from requests import RequestException


def get_all_labels(owner, repo, token):
    labels_url = f"https://api.github.com/repos/{owner}/{repo}/labels"
    headers = {'Authorization': f'token {token}'}
    labels = []
    page = 1
    per_page = 100
    while True:
        try:
            params = {'page': page, 'per_page': per_page}
            labels_response = requests.get(labels_url, params=params, headers=headers)
            if labels_response.status_code == 200:
                labels_data = labels_response.json()
                if not labels_data:
                    break
                labels.extend(labels_data)
                if len(labels) > 1000:
                    break
                page += 1
        except RequestException as e:
            print(f"An error occurred while fetching repos : {e}")
            return None
    return labels
