"""
GitHub Pull Request Integration
Automatically create pull requests with trust analysis reports
"""

import base64
from datetime import datetime
import json
import os
import re
import time
from urllib.parse import quote

import requests

def create_pull_request(owner, repo, token):
    """
    Create a pull request with the trust analysis report
    
    Args:
        owner: Repository owner
        repo: Repository name
        token: GitHub personal access token
        
    Returns:
        URL of the created pull request
    """
    
    # Read the generated report
    readme_path = f'../docs/README_{repo}.md'
    details_path = f'../docs/Metrics_detail_template_Component_(Integrity)_{repo}.md'
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    with open(details_path, 'r', encoding='utf-8') as f:
        details_content = f.read()
    
    # Update image paths for repo root and collect image files to upload.
    image_matches = []
    image_matches.extend(re.findall(r"\.\./images/([^\")]+)", readme_content))
    image_matches.extend(re.findall(r"\.\./assets/grades/([^\")]+)", readme_content))
    readme_content = readme_content.replace("../images/", "images/")
    readme_content = readme_content.replace("../assets/grades/", "assets/grades/")

    # GitHub API headers
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # 1. Get the default branch from the upstream repo
    repo_url = f'https://api.github.com/repos/{owner}/{repo}'
    response = requests.get(repo_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch repo info: {response.status_code} {response.text}")
    default_branch = response.json().get('default_branch')
    if not default_branch:
        raise Exception(f"Repo info missing default_branch: {response.text}")

    # 2. Get authenticated user (fork owner)
    user_url = 'https://api.github.com/user'
    response = requests.get(user_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch user info: {response.status_code} {response.text}")
    fork_owner = response.json().get('login')
    if not fork_owner:
        raise Exception(f"User info missing login: {response.text}")

    # 3. Ensure fork exists
    fork_url = f'https://api.github.com/repos/{owner}/{repo}/forks'
    response = requests.post(fork_url, headers=headers)
    if response.status_code not in [202, 201]:
        raise Exception(f"Failed to fork repo: {response.status_code} {response.text}")

    # 4. Wait for fork to be ready
    fork_repo_url = f'https://api.github.com/repos/{fork_owner}/{repo}'
    fork_ready = False
    for _ in range(10):
        response = requests.get(fork_repo_url, headers=headers)
        if response.status_code == 200:
            fork_ready = True
            break
        time.sleep(1)
    if not fork_ready:
        raise Exception("Fork is not ready yet. Please try again in a moment.")
    
    # 5. Get the latest commit SHA of default branch in the fork
    ref_url = f'https://api.github.com/repos/{fork_owner}/{repo}/git/refs/heads/{default_branch}'
    response = requests.get(ref_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch default branch ref: {response.status_code} {response.text}")
    base_sha = response.json().get('object', {}).get('sha')
    if not base_sha:
        raise Exception(f"Default branch ref missing sha: {response.text}")
    
    # 6. Create a new branch in the fork
    branch_name = f'trust-analysis-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
    create_ref_url = f'https://api.github.com/repos/{fork_owner}/{repo}/git/refs'
    create_ref_data = {
        'ref': f'refs/heads/{branch_name}',
        'sha': base_sha
    }
    response = requests.post(create_ref_url, headers=headers, json=create_ref_data)
    
    if response.status_code != 201:
        raise Exception(f"Failed to create branch: {response.text}")
    
    # 7. Create/Update files in the new branch
    files_to_create = [
        {
            'path': 'TRUST_ANALYSIS.md',
            'content': readme_content,
            'message': 'Add SocialTrust analysis report'
        },
        {
            'path': 'TRUST_ANALYSIS_DETAILED.md',
            'content': details_content,
            'message': 'Add detailed trust metrics'
        }
    ]

    for image_rel_path in image_matches:
        if image_rel_path.startswith("grade_"):
            local_path = os.path.join('..', 'assets', 'grades', image_rel_path)
            repo_path = f'assets/grades/{image_rel_path}'
        else:
            local_path = os.path.join('..', 'images', image_rel_path)
            repo_path = f'images/{image_rel_path}'
        if not os.path.exists(local_path):
            continue
        files_to_create.append({
            'path': repo_path,
            'binary_path': local_path,
            'message': f'Add SocialTrust image: {image_rel_path}'
        })
    
    for file_info in files_to_create:
        # Check if file exists
        encoded_path = quote(file_info["path"])
        file_url = f'https://api.github.com/repos/{fork_owner}/{repo}/contents/{encoded_path}'
        response = requests.get(file_url, headers=headers, params={'ref': branch_name})

        if 'binary_path' in file_info:
            with open(file_info['binary_path'], 'rb') as f:
                encoded_content = base64.b64encode(f.read()).decode()
        else:
            encoded_content = base64.b64encode(file_info['content'].encode()).decode()

        file_data = {
            'message': file_info['message'],
            'content': encoded_content,
            'branch': branch_name
        }
        
        if response.status_code == 200:
            # File exists, update it
            file_data['sha'] = response.json()['sha']
        
        response = requests.put(file_url, headers=headers, json=file_data)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create/update file {file_info['path']}: {response.text}")
    
    # 8. Create pull request within the fork
    pr_url = f'https://api.github.com/repos/{fork_owner}/{repo}/pulls'
    pr_data = {
        'title': 'Add SocialTrust Report',
        'body': f'''SocialTrust report is an auto-generated markdown file that presents the percentile rankings of summarized statistics such as contributor participation, usage popularity, and issue maintenance. We created SocialTrust to help open-source consumers understand whether their dependencies are safe and to assist open-source maintainers in improving their repository management.''',
        'head': branch_name,
        'base': default_branch
    }
    
    response = requests.post(pr_url, headers=headers, json=pr_data)
    
    if response.status_code != 201:
        raise Exception(f"Failed to create pull request: {response.text}")
    
    pr_info = response.json()
    return pr_info['html_url']
