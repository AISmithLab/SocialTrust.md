import json
import os

from api.code_of_conduct import get_code_of_conduct
from api.comments import get_comments
from api.commits import get_all_commits, get_commit_by_sha
from api.contributing import get_contributing
from api.dependencies import get_dependencies_count, get_all_dependencies, get_outdated_dependencies_count
from api.dependents import get_dependents_repositories_count
from api.governance import get_governance
from api.issues import get_recent_issues, get_issues_rate
from api.labels import get_all_labels
from api.maintainers import get_all_repos_from_maintainer
from api.profile import get_profile
from api.pulls import get_recent_pull_requests, get_pulls_rate
from api.readme import get_readme
from api.release import get_releases
from api.repositories import get_repo_info
from api.scorecard import get_scorecard_data
from api.workflow import get_workflow

# dir_path = "/Users/zhangyujin/PycharmProjects/oss-percentile"

dir_path = ".."

def scrape(owner, repo, token):

    if not os.path.exists(f"{dir_path}/data/{owner}_{repo}"):
        os.mkdir(f"{dir_path}/data/{owner}_{repo}")
        os.mkdir(f"{dir_path}/data/{owner}_{repo}/commits")
        os.mkdir(f"{dir_path}/data/{owner}_{repo}/comments")

    # Maintenance and Goodwill

    # health percentage

    profile_data = get_profile(owner, repo, token)
    if profile_data:
        with open(f"{dir_path}/data/{owner}_{repo}/profile.json", "w") as f:
            json.dump(profile_data, f, indent=4)

    # readme

    readme_data = get_readme(owner, repo, token)
    if readme_data:
        with open(f"{dir_path}/data/{owner}_{repo}/README.md", "w") as f:
            f.write(readme_data)

    # governance

    governance_data = get_governance(owner, repo, token)
    if governance_data:
        with open(f"{dir_path}/data/{owner}_{repo}/governance.md", "w") as f:
            f.write(governance_data)

    # contributing

    contributing_data = get_contributing(owner, repo, token)
    if contributing_data:
        with open(f"{dir_path}/data/{owner}_{repo}/contributing.md", "w") as f:
            f.write(contributing_data)

    # code-of-conduct
    code_of_conduct_data = get_code_of_conduct(owner, repo, token)
    if code_of_conduct_data:
        with open(f"{dir_path}/data/{owner}_{repo}/code-of-conduct.md", "w") as f:
            f.write(code_of_conduct_data)

    # labels

    labels_data = get_all_labels(owner, repo, token)
    if labels_data:
        with open(f"{dir_path}/data/{owner}_{repo}/labels.json", "w") as f:
            json.dump(labels_data, f, indent=4)


    # Code Quality

    # web-info:
    issues_rate_data = get_issues_rate(owner, repo)
    if issues_rate_data:
        with open(f"{dir_path}/data/{owner}_{repo}/issues_rate.json", 'w') as f:
            json.dump(issues_rate_data, f, indent=4)

    pulls_rate_data = get_pulls_rate(owner, repo)
    if pulls_rate_data:
        with open(f"{dir_path}/data/{owner}_{repo}/pulls_rate.json", 'w') as f:
            json.dump(pulls_rate_data, f, indent=4)

    # maintainer
    maintainer_data = get_all_repos_from_maintainer(owner, token)
    if maintainer_data:
        with open(f"{dir_path}/data/{owner}_{repo}/maintainer.json", "w") as f:
            json.dump(maintainer_data, f, indent=4)

    # scorecard
    scorecard_data = get_scorecard_data(owner, repo)
    if scorecard_data:
        with open(f"{dir_path}/data/{owner}_{repo}/scorecard.json", "w") as f:
            json.dump(scorecard_data, f, indent=4)

    # workflow
    workflow_data = get_workflow(owner, repo, token)
    if workflow_data:
        with open(f"{dir_path}/data/{owner}_{repo}/workflow.json", "w") as f:
            json.dump(workflow_data, f, indent=4)
        
    # dependents and dependencies

    dependents = get_dependents_repositories_count(owner, repo)
    dependencies = get_dependencies_count(owner, repo)
    dependencies_data = get_all_dependencies(owner, repo)
    outdated_dependencies = get_outdated_dependencies_count(dependencies_data, token)
    data = {
        'dependencies': dependencies,
        'dependents': dependents,
        'dependencies_version_staleness' : outdated_dependencies
    }
    with open(f"{dir_path}/data/{owner}_{repo}/dependency_graph.json", "w") as f:
        json.dump(data, f, indent=4)

    # versions
    release_data = get_releases(owner, repo, token)
    if release_data:
        with open(f"{dir_path}/data/{owner}_{repo}/releases.json", "w") as f:
            json.dump(release_data, f, indent=4)

    # Community Activity and Integrity

    # repo_info: stars_and_watchers, forks
    repo_data = get_repo_info(owner, repo, token)
    if repo_data:
        with open(f"{dir_path}/data/{owner}_{repo}/repo.json", "w") as f:
            json.dump(repo_data, f, indent=4)

    # issues and comments: issues_reporters_count,  issue_closed_rate, issue_time_to_close
    issues_data = get_recent_issues(owner, repo, token)
    if issues_data:
        with open(f"{dir_path}/data/{owner}_{repo}/issues.json", "w") as f:
            json.dump(issues_data, f, indent=4)
        for issue in issues_data:
            comment_data = get_comments(owner, repo, token, issue['comments_url'])
            if comment_data:
                with open(f"{dir_path}/data/{owner}_{repo}/comments/{issue['number']}.json", "w") as f:
                    json.dump(comment_data, f, indent=4)

    # pulls and comments: submitted_PRs
    pulls_data = get_recent_pull_requests(owner, repo, token)
    if pulls_data:
        with open(f"{dir_path}/data/{owner}_{repo}/pulls.json", "w") as f:
            json.dump(pulls_data, f, indent=4)
        for pull in pulls_data:
            comment_data = get_comments(owner, repo, token, pull['comments_url'])
            if comment_data:
                with open(f"{dir_path}/data/{owner}_{repo}/comments/{pull['number']}.json", "w") as f:
                    json.dump(comment_data, f, indent=4)

    # commits:  submitted_commmits, contributors_count,
    commits_data = get_all_commits(owner, repo, token)
    if commits_data:
        with open(f"{dir_path}/data/{owner}_{repo}/commits.json", "w") as f:
            json.dump(commits_data, f, indent=4)
        for commit in commits_data:
            commit_data = get_commit_by_sha(owner, repo, token, commit["sha"])
            if commit_data:
                with open(f"{dir_path}/data/{owner}_{repo}/commits/{commit['sha']}.json", "w") as f:
                    json.dump(commit_data, f, indent=4)


# if __name__ == '__main__':
#     owner = ""
#     repo = ""
#     token = ""
#     scrape(owner, repo, token)
