import requests


def get_scorecard_data(owner, repo):
    scorecard_url = f"https://api.securityscorecards.dev/projects/github.com/{owner}/{repo}"
    scorecard_response = requests.get(scorecard_url)

    if scorecard_response.status_code == 200:
        return scorecard_response.json()
    else:
        print(f"Failed to retrieve scorecard. Status code: {scorecard_response.status_code}")
        return None
