import requests
from requests import RequestException


def get_profile(owner, repo, token):
    profile_url = f"https://api.github.com/repos/{owner}/{repo}/community/profile"
    headers = {'Authorization': f'token {token}'}
    try:
        profile_response = requests.get(profile_url, headers=headers)
        return profile_response.json()
    except RequestException as e:
        print(f"An error occurred while fetching profile : {e}")
        return None
