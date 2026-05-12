import re

import requests
from bs4 import BeautifulSoup
from requests import RequestException

from api.release import get_releases


def get_dependencies_count(owner, repo):
    url = f"https://github.com/{owner}/{repo}/network/dependencies?page={1}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "html.parser")
            # Find the div element that contains the text "Total"
            total_div = soup.find("div", class_="Box-header d-flex")
            if total_div and "Total" in total_div.text:
                first_word = total_div.text.strip().split()[0]
                number = int(first_word.replace(",", ""))
                # print(number)
                return number
            else:
                print("No matching content found")
        else:
            print(f"Request failed with status code: {r.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return 0


def extract_version_number(text):
    version_pattern = r'(\*|\d+)\.(\*|\d+)\.(\*|\d+)'
    match = re.search(version_pattern, text)
    if match:
        return match.group(0)
    return None


def is_version_match(specific_version, wildcard_version):
    specific_parts = specific_version.split('.')
    wildcard_parts = wildcard_version.split('.')
    length = len(wildcard_parts)
    for i in range(0, length):
        if specific_parts[i] == wildcard_parts[i] or wildcard_parts[i] == '*':
            continue
        return False
    return True


def get_all_dependencies(owner, repo):
    dependencies = []
    flag = True
    page_num = 1
    while flag:
        url = f"https://github.com/{owner}/{repo}/network/dependencies?page={page_num}"
        try:
            r = requests.get(url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, "html.parser")
                dependency_repos = soup.find_all('a', {'data-hovercard-type': 'dependendency_graph_package'})
                if not dependency_repos:
                    flag = False
                    break
                for item in dependency_repos:
                    repo_name = item.text.strip()
                    version = item.find_next_sibling('span').text.strip()
                    href = item.get('href')
                    package_json_url = item.find_next('a', {'data-test-selector': 'dg-repo-pkg-manifest'})['href']
                    exists = any(item["name"] == repo_name for item in dependencies)
                    if exists:
                        continue
                    try:
                        response = requests.get(f"https://github.com{package_json_url}", allow_redirects=False)
                        if response.status_code == 200:
                            data = {
                                "name": f"{repo_name}",
                                "version": f"{version}",
                                "url": f"https://github.com{href}",
                            }
                            dependencies.append(data)
                    except RequestException as e:
                        print(f"An error occurred while fetching dependencies: {e}. Skipping this issue.")
        except RequestException as e:
            print(f"An error occurred while fetching dependencies: {e}. Skipping this issue.")
        page_num += 1
    return dependencies


def get_outdated_dependencies_count(dependencies, token):
    outdated_sum = 0
    for dependency in dependencies:
        version = extract_version_number(dependency['version'])
        if version:
            url = dependency['url']
            release_owner = url.split("/")[3]
            release_repo = url.split("/")[4]
            if release_repo == "common-tags":
                continue
            try:
                releases = get_releases(release_owner, release_repo, token)
                if releases:
                    for release in releases:
                        release_version = extract_version_number(release['tag_name'])
                        if release_version:
                            if is_version_match(release_version, version):
                                break
                            else:
                                outdated_sum += 1
                        else:
                            continue
            except RequestException as e:
                print(f"An error occurred while fetching dependencies: {e}. Skipping this issue.")

    return outdated_sum
