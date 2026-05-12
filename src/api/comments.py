import requests
import time


def get_comments(owner, repo, token, comments_url):
    headers = {'Authorization': f'token {token}'}
    while True:
        try:
            comments_response = requests.get(comments_url, headers=headers)
            if comments_response.status_code == 200:
                return comments_response.json()
            else:
                print(f"Failed to retrieve comments. Status code: {comments_response.status_code} Retrying in 5 seconds...")
                time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying in {5} seconds...")
            time.sleep(5)
