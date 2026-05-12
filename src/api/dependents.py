import requests
from bs4 import BeautifulSoup


def get_dependents(owner, repo, token):
    dependents_url = f"https://api.github.com/repos/{owner}/{repo}/dependents"
    headers = {'Authorization': f'token {token}'}
    dependents_response = requests.get(dependents_url, headers=headers)
    if dependents_response.status_code == 200:
        return dependents_response.json()
    elif dependents_response.status_code == 404:
        return []
    else:
        print(f"Failed to retrieve dependents. Status code: {dependents_response.status_code}")
        return None

def get_dependents_repositories_count(owner, repo):
    url = f"https://github.com/{owner}/{repo}/network/dependents?page={1}"
    # print(url)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "html.parser")
            text = soup.find_all("a")
            for link in text:
                if "Host and manage packages" in link.text:
                    continue
                if "Repositories" in link.text:
                    # print(link)
                    first_word = link.text.strip().split()[0]
                    number = int(first_word.replace(",", ""))
                    # print(number)
                    return number
        else:
            print(f"Request failed with status code: {r.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return 0


def get_dependents_packages_count(owner, repo):
    url = f"https://github.com/{owner}/{repo}/network/dependents?page={1}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "html.parser")
            text = soup.find_all("a")
            for link in text:
                if "Host and manage packages" in link.text:
                    continue
                if  "Packages" in link.text:
                    # print(link)
                    first_word = link.text.strip().split()[0]
                    number = int(first_word.replace(",", ""))
                    # print(number)
                    return number
        else:
            print(f"Request failed with status code: {r.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return 0


# if __name__ == '__main__':
    # get_dependents_repositories_count('chalk', 'chalk')
    # get_dependents_packages_count('chalk', 'chalk')
