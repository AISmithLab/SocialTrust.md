import csv

import pandas as pd
import os
import re
import json
from collections import defaultdict
from datetime import datetime, timezone
import pytz


def safe_int(value, default=pd.NA):
    if value is None or value is pd.NA:
        return default
    if isinstance(value, float) and pd.isna(value):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def initialize(metrics_path):
    metrics = {
        'repo': pd.Series([None], dtype='object'),
        'owner': pd.Series([None], dtype='object'),
        'stars': pd.Series([None], dtype='Int64'),  # Number of stars
        'watchers': pd.Series([None], dtype='Int64'),  # Number of watchers
        'forks': pd.Series([None], dtype='Int64'),  # Number of forks
        'downstream_dependents': pd.Series([None], dtype='Int64'),  # Number of downstream dependents
        'distinct_contributors_7m': pd.Series([None], dtype='Int64'),  # Number of distinct contributors (7 months)
        'issue_reporters_7m': pd.Series([None], dtype='Int64'),  # Number of issue reporters (7 months)
        'comments_per_commit_7m': pd.Series([None], dtype='float64'),  # Number of comments per commit (7 months)
        'average_comment_length_7m': pd.Series([None], dtype='float64'),  # Average length of comments (7 months)
        'submitted_PRs_7m': pd.Series([None], dtype='Int64'),  # Number of submitted PRs (7 months)
        'commits_pushed_7m': pd.Series([None], dtype='Int64'),  # Number of commits pushed (7 months)
        'active_contributor_growth_7m': pd.Series([None], dtype='Int64'),  # Change in number of active contributors (7 months)
        'issues_closed_percentage': pd.Series([None], dtype='float64'),  # Percentage of issues closed
        'time_to_close_issues_7m': pd.Series([None], dtype='float64'),  # Average time to close issues (7 months)
        'time_first_comment_issues_7m': pd.Series([None], dtype='float64'),  # Average time until first maintainers comment on issues (7 months)
        'PRs_closed_percentage': pd.Series([None], dtype='float64'),  # Percentage of PRs closed
        'time_to_close_PRs_7m': pd.Series([None], dtype='float64'),  # Time to close PRs (7 months)
        'time_first_comment_close_PRs_7m': pd.Series([None], dtype='float64'),  # Time until first maintainer comment or close on PRs (7 months)
        'commits_7m': pd.Series([None], dtype='Int64'),  # Number of commits (7 months)
        'labels': pd.Series([None], dtype='Int64'),  # Number of labels (7 months)
        'community_health_percentage': pd.Series([None], dtype='float64'),  # Health percentage
        'headings_code_of_conduct': pd.Series([None], dtype='Int64'),  # Number of headings in code of conduct
        'headings_contributing': pd.Series([None], dtype='Int64'),  # Number of headings in contributing
        'headings_governance': pd.Series([None], dtype='Int64'),  # Number of headings in governance documents
        'headings_README': pd.Series([None], dtype='Int64'),  # Number of headings in README
        'projects_owned_per_maintainer': pd.Series([None], dtype='float64'),  # Average number of projects owned by each maintainer
        'median_age_other_projects': pd.Series([None], dtype='float64'),  # Median age of other projects owned by each maintainer
        'dependencies_version_staleness': pd.Series([None], dtype='float64'),  # Dependencies version staleness
        'number_of_dependencies': pd.Series([None], dtype='Int64'),  # Number of dependencies
        'dependencies_with_vulnerabilities': pd.Series([None], dtype='Int64'),  # Number of dependencies with unaddressed vulnerabilities
        'check_runs': pd.Series([None], dtype='Int64'),  # Number of check runs
        'workflow_runs': pd.Series([None], dtype='Int64'),  # Number of workflow runs
        'distinct_people_closed_PRs_7m': pd.Series([None], dtype='Int64'),  # Distinct number of people who closed PRs (7 months)
        'contributors_per_code_file': pd.Series([None], dtype='float64'),  # Number of contributors per code file
        'files_with_2plus_contributors': pd.Series([None], dtype='float64'),  # Percentage of files with 2+ contributors
        'time_since_created': pd.Series([None], dtype='float64'),  # Time since created
        'number_of_versions': pd.Series([None], dtype='Int64')  # Number of versions
    }

    df = pd.DataFrame(metrics)
    df.to_csv(metrics_path, index=False)


def calculate(owner, repo, metrics_path, repos_data_path):
    metrics = pd.read_csv(metrics_path, dtype={'repo': 'object', 'owner': 'object'})
    july_aware = datetime(2023, 7, 1, tzinfo=pytz.utc)
    jan_aware = datetime(2024, 1, 31, tzinfo=pytz.utc)

    metrics.at[0, 'repo'] = repo
    metrics.at[0, 'owner'] = owner
    metrics.to_csv(metrics_path, index=False)

    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        repo_path = f"{repos_data_path}/{owner}_{repo}"
        if os.path.exists(repo_path):
            # print(repo_path)
            repo_info_path = f"{repos_data_path}/{owner}_{repo}/repo.json"
            if os.path.exists(repo_info_path):
                # print(repo_info_path)
                with open(repo_info_path, 'r') as f:
                    repo_info = json.load(f)
                metrics.at[index, 'stars'] = safe_int(repo_info.get('stargazers_count', 0), 0)
                metrics.at[index, 'forks'] = safe_int(repo_info.get('forks_count', 0), 0)
                metrics.at[index, 'watchers'] = safe_int(repo_info.get('watchers', 0), 0)
                created_date = datetime.strptime(repo_info.get('created_at'), "%Y-%m-%dT%H:%M:%SZ")
                current_date = datetime.utcnow()
                days_difference = (current_date - created_date).days
                metrics.at[index, 'time_since_created'] = float(f"{days_difference:.1f}")

    metrics.to_csv(metrics_path, index=False)

    # dependency graph
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        repo_path = f"{repos_data_path}/{owner}_{repo}"
        if os.path.exists(repo_path):
            # print(repo_path)
            repo_info_path = f"{repos_data_path}/{owner}_{repo}/dependency_graph.json"
            if os.path.exists(repo_info_path):
                # print(repo_info_path)
                with open(repo_info_path, 'r') as f:
                    repo_info = json.load(f)
                metrics.at[index, 'downstream_dependents'] = safe_int(repo_info.get('dependents', 0), 0)
                metrics.at[index, 'number_of_dependencies'] = safe_int(repo_info.get('dependencies', 0), 0)
                metrics.at[index, 'dependencies_version_staleness'] = float(repo_info.get('dependencies_version_staleness', 0))

    metrics.to_csv(metrics_path, index=False)

    # commits
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        commits_path = f"{repos_data_path}/{owner}_{repo}/commits.json"
        contributors = set()
        commit_count = 0
        comment_count = 0
        if os.path.exists(commits_path):
            with open(commits_path, 'r') as f:
                commits = json.load(f)
            if commits is None:
                continue
            for commit in commits:
                date_str = commit['commit']['author']['date']
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_obj_aware = date_obj.replace(tzinfo=pytz.utc)
                if date_obj_aware > july_aware and date_obj_aware < jan_aware:
                    commit_count += 1
                    comment_count += commit['commit']['comment_count']
                    contributors.add(commit['commit']['author']['name'])
        metrics.at[index, 'commits_pushed_7m'] = commit_count if commit_count > 0 else pd.NA
        metrics.at[index, 'commits_7m'] = commit_count if commit_count > 0 else pd.NA
        metrics.at[index, 'comments_per_commit_7m'] = (comment_count / commit_count) if commit_count > 0 else pd.NA
        metrics.at[index, 'distinct_contributors_7m'] = len(contributors) if len(contributors) > 0 else pd.NA

    metrics.to_csv(metrics_path, index=False)

    # issues
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        issues_path = f"{repos_data_path}/{owner}_{repo}/issues.json"
        if os.path.exists(issues_path):
            closed_issues_count = 0
            commented_issues_count = 0
            total_comments = 0
            total_time_to_comment = 0
            total_time_to_close = 0
            participants = set()
            issues_count = 0
            comment_length = 0
            comment_count = 0

            with open(issues_path, 'r') as f:
                issues = json.load(f)

            for issue in issues:
                created_at = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                date_str = issue['created_at']
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_obj_aware = date_obj.replace(tzinfo=pytz.utc)
                if date_obj_aware > july_aware and date_obj_aware < jan_aware:
                    issues_count += 1
                    if issue.get('user'):
                        participants.add(issue['user']['login'])
                    issues_count += 1
                    if issue['state'] == 'closed':
                        closed_issues_count += 1
                        closed_at = datetime.strptime(issue['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
                        total_time_to_close += (closed_at - created_at).total_seconds()
                    comments_path = f"{repos_data_path}/{owner}_{repo}/comments/{issue['number']}.json"
                    if os.path.exists(comments_path):
                        with open(comments_path, 'r') as f:
                            comments = json.load(f)
                            first_comment_time = datetime.strptime(comments[0]['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                            time_to_comment = (first_comment_time - created_at).total_seconds()
                            total_time_to_comment += time_to_comment
                            commented_issues_count += 1
                            for comment in comments:
                                comment_length += len(comment['body'])
                                comment_count += 1
            metrics.at[index, 'issue_reporters_7m'] = len(participants)
            metrics.at[index, 'time_to_close_issues_7m'] = (total_time_to_close / closed_issues_count / (24 * 3600)) if closed_issues_count > 0 else pd.NA
            metrics.at[index, 'time_first_comment_issues_7m'] = (total_time_to_comment / commented_issues_count / (24 * 3600)) if commented_issues_count > 0 else pd.NA
            metrics.at[index, 'average_comment_length_7m'] = (comment_length / comment_count) if comment_count > 0 else pd.NA

    metrics.to_csv(metrics_path, index=False)

    # pulls
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        pulls_path = f"{repos_data_path}/{owner}_{repo}/pulls.json"
        if os.path.exists(pulls_path):
            pulls_count = 0
            closed_pulls_count = 0
            merged_pulls_count = 0
            commented_pulls_count = 0
            total_comments = 0
            total_time_to_comment = 0
            total_time_to_close = 0
            # monthly_pulls_count = defaultdict(int)
            participants = set()
            with open(pulls_path, 'r') as f:
                pulls = json.load(f)
            if pulls is None:
                continue
            for pull in pulls:
                created_at = datetime.strptime(pull['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                date_str = pull['created_at']
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_obj_aware = date_obj.replace(tzinfo=pytz.utc)
                if date_obj_aware > july_aware and date_obj_aware < jan_aware:
                    pulls_count += 1
                    if pull['state'] == 'closed':
                        author = pull['user']['login']
                        participants.add(author)
                        closed_pulls_count += 1
                        closed_at = datetime.strptime(pull['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
                        total_time_to_close += (closed_at - created_at).total_seconds()
                    comments_path = f"{repos_data_path}/{owner}_{repo}/comments/{pull['number']}.json"
                    if os.path.exists(comments_path):
                        with open(comments_path, 'r') as f:
                            comments = json.load(f)
                            first_comment_time = datetime.strptime(comments[0]['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                            time_to_comment = (first_comment_time - created_at).total_seconds()
                            total_time_to_comment += time_to_comment
                            commented_pulls_count += 1
            metrics.at[index, 'distinct_people_closed_PRs_7m'] = len(participants)
            metrics.at[index, 'submitted_PRs_7m'] = pulls_count
            metrics.at[index, 'time_to_close_PRs_7m'] = (total_time_to_close / closed_pulls_count / (24 * 3600)) if closed_pulls_count > 0 else pd.NA
            metrics.at[index, 'time_first_comment_close_PRs_7m'] = (total_time_to_comment / commented_pulls_count / (24 * 3600)) if commented_pulls_count > 0 else pd.NA

    metrics.to_csv(metrics_path, index=False)

    # labels
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        labels_path = f"{repos_data_path}/{owner}_{repo}/labels.json"
        if os.path.exists(labels_path):
            with open(labels_path, 'r') as f:
                labels = json.load(f)
        metrics.at[index, 'labels'] = len(labels) if labels else 0

    metrics.to_csv(metrics_path, index=False)

    # issue and pull rate
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        open_issues = 0
        closed_issues = 0
        issues_rate_path = f"{repos_data_path}/{owner}_{repo}/issues_rate.json"
        if os.path.exists(issues_rate_path):
            with open(issues_rate_path, 'r') as f:
                issues_rate = json.load(f)
            open_issues = issues_rate.get('open_issues', 0)
            closed_issues = issues_rate.get('closed_issues', 0)
            metrics.at[index, 'issues_closed_percentage'] = (closed_issues / (open_issues + closed_issues)) if open_issues + closed_issues > 0 else pd.NA
        open_pulls = 0
        closed_pulls = 0
        pulls_rate_path = f"{repos_data_path}/{owner}_{repo}/pulls_rate.json"
        if os.path.exists(pulls_rate_path):
            with open(pulls_rate_path, 'r') as f:
                pulls_rate = json.load(f)
            open_pulls = pulls_rate.get('open_pulls', 0)
            closed_pulls = pulls_rate.get('closed_pulls', 0)
            metrics.at[index, 'PRs_closed_percentage'] = (closed_pulls / (open_pulls + closed_pulls)) if (open_pulls + closed_pulls) > 0 else pd.NA

    metrics.to_csv(metrics_path, index=False)

    # health
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        profile_path = f"{repos_data_path}/{owner}_{repo}/profile.json"
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = json.load(f)
            metrics.at[index, 'community_health_percentage'] = safe_int(profile.get('health_percentage'), pd.NA) if profile else pd.NA

    metrics.to_csv(metrics_path, index=False)

    # maintainers
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        maintainer_path = f"{repos_data_path}/{owner}_{repo}/maintainer.json"
        today = datetime.strptime("2024-01-31T23:59:59Z", '%Y-%m-%dT%H:%M:%SZ')
        age = 0
        if os.path.exists(maintainer_path):
            with open(maintainer_path, 'r') as f:
                maintainer = json.load(f)
            for repo in maintainer:
                if isinstance(repo, dict):
                    created_at = datetime.strptime(repo['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                    if created_at < today:
                        age += (today - created_at).total_seconds()
        metrics.at[index, 'projects_owned_per_maintainer'] = len(maintainer) if maintainer else pd.NA
        metrics.at[index, 'median_age_other_projects'] = (age / len(maintainer) / (3600 * 24)) if maintainer else pd.NA

    # check run
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        workflow_path = f"{repos_data_path}/{owner}_{repo}/workflow.json"
        if os.path.exists(workflow_path):
            with open(workflow_path, 'r') as f:
                workflow = json.load(f)
        # print(workflow['total_count'])
        metrics.at[index, 'check_runs'] = safe_int(workflow.get('total_count'), pd.NA) if workflow else pd.NA
        metrics.at[index, 'workflow_runs'] = safe_int(workflow.get('total_count'), pd.NA) if workflow else pd.NA

    metrics.to_csv(metrics_path, index=False)

    # versions
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        releases_path = f"{repos_data_path}/{owner}_{repo}/releases.json"
        if os.path.exists(releases_path):
            with open(releases_path, 'r') as f:
                releases = json.load(f)
            metrics.at[index, 'number_of_versions'] = len(releases) if releases else pd.NA

    metrics.to_csv(metrics_path, index=False)

    # contributors_per_code_file & files_with_2plus_contributors
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        commits_path = f"{repos_data_path}/{owner}_{repo}/commits.json"
        if os.path.exists(commits_path):
            with open(commits_path, 'r') as f:
                commits = json.load(f)
            if commits is None:
                continue
            file_contributors = {}
            for commit in commits:
                commit_sha = commit['sha']
                commit_path = f"{repos_data_path}/{owner}_{repo}/commits/{commit_sha}.json"
                if os.path.exists(commit_path):
                    with open(commit_path, 'r') as f:
                        commit_data = json.load(f)
                    if commit_data.get('author'):
                        author = commit_data['author']['login']
                        for file in commit_data['files']:
                            filename = file['filename']
                            if filename not in file_contributors:
                                file_contributors[filename] = set()
                            file_contributors[filename].add(author)
            total_contributors = 0
            total_files = 0
            files_with_more_than_1_contributors = 0
            for contributors in file_contributors.values():
                total_contributors += len(contributors)
                total_files += 1
                if len(contributors) > 1:
                    files_with_more_than_1_contributors += 1
            # num_files = len(file_contributors)
            metrics.at[index, 'contributors_per_code_file'] = (total_contributors / total_files) if total_files > 0 else pd.NA
            metrics.at[index, 'files_with_2plus_contributors'] = files_with_more_than_1_contributors if files_with_more_than_1_contributors > 0 else pd.NA

    metrics.to_csv(metrics_path, index=False)

    # active_contributor_growth_7m
    for index, row in metrics.iterrows():
        dec_aware = datetime(2023, 12, 1, tzinfo=pytz.utc)
        jan_aware = datetime(2024, 1, 1, tzinfo=pytz.utc)
        feb_aware = datetime(2024, 2, 1, tzinfo=pytz.utc)
        owner = row['owner']
        repo = row['repo']
        commits_count = 0
        pulls_path = f"{repos_data_path}/{owner}_{repo}/pulls.json"
        if os.path.exists(pulls_path):
            with open(pulls_path, 'r') as f:
                pulls = json.load(f)
            if pulls is None:
                continue
            dec_authors = set()
            jan_authors = set()
            for pull in pulls[:500]:
                author = pull['user']['login']
                date_str = pull['created_at']
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_obj_aware = date_obj.replace(tzinfo=pytz.utc)
                if date_obj_aware > dec_aware and date_obj_aware < jan_aware:
                    dec_authors.add(author)
                elif date_obj_aware > jan_aware and date_obj_aware < feb_aware:
                    jan_authors.add(author)
            metrics.at[index, 'active_contributor_growth_7m'] = len(jan_authors) - len(dec_authors)

    metrics.to_csv(metrics_path, index=False)

    # headings
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        heading_levels = {
            'h1': re.compile(r'^(#\s.*)', re.MULTILINE),
            'h2': re.compile(r'^(##\s.*)', re.MULTILINE),
            'h3': re.compile(r'^(###\s.*)', re.MULTILINE)
        }
        readme_path = f"{repos_data_path}/{owner}_{repo}/README.md"
        counts = 0
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as file:
                for line in file:
                    for level, regex in heading_levels.items():
                        matches = regex.findall(line)
                        counts += len(matches)
        metrics.at[index, 'headings_README'] = safe_int(counts, 0)

        contributing_path = f"{repos_data_path}/{owner}_{repo}/CONTRIBUTING.md"
        counts = 0
        if os.path.exists(contributing_path):
            with open(contributing_path, 'r', encoding='utf-8') as file:
                for line in file:
                    for level, regex in heading_levels.items():
                        matches = regex.findall(line)
                        counts += len(matches)
        metrics.at[index, 'headings_contributing'] = safe_int(counts, 0)

        code_of_conduct_path = f"{repos_data_path}/{owner}_{repo}/code-of-conduct.md"
        counts = 0
        if os.path.exists(code_of_conduct_path):
            with open(code_of_conduct_path, 'r', encoding='utf-8') as file:
                for line in file:
                    for level, regex in heading_levels.items():
                        matches = regex.findall(line)
                        counts += len(matches)
        metrics.at[index, 'headings_code_of_conduct'] = safe_int(counts, 0)

        governance_path = f"{repos_data_path}/{owner}_{repo}/governance.md"
        counts = 0
        if os.path.exists(governance_path):
            with open(governance_path, 'r', encoding='utf-8') as file:
                for line in file:
                    for level, regex in heading_levels.items():
                        matches = regex.findall(line)
                        counts += len(matches)
        metrics.at[index, 'headings_governance'] = safe_int(counts, 0)

    metrics.to_csv(metrics_path, index=False)

    # vulnerabilities
    for index, row in metrics.iterrows():
        owner = row['owner']
        repo = row['repo']
        scorecard = None
        scorecard_path = f"{repos_data_path}/{owner}_{repo}/scorecard.json"
        if os.path.exists(scorecard_path):
            with open(scorecard_path, 'r') as f:
                scorecard = json.load(f)
        checks = scorecard.get('checks') if isinstance(scorecard, dict) else None
        if checks:
            for check in checks:
                if check['name'] == "Vulnerabilities":
                    value = check['reason'].split()[0]
                    metrics.at[index, 'dependencies_with_vulnerabilities'] = value if value.isdigit() else pd.NA

    metrics.to_csv(metrics_path, index=False)


def merge_files(metrics_file, input_file, output_file):
    try:
        with open(metrics_file, mode='r', newline='') as metrics_infile:
            metrics_reader = csv.DictReader(metrics_infile)
            metrics_row = next(metrics_reader) 

            new_row = {
                'repo': metrics_row['repo'],
                'owner': metrics_row['owner'],
                'Stars+watchers': safe_int(metrics_row['stars'], 0) + safe_int(metrics_row['watchers'], 0),
                'forks': metrics_row['forks'],
                'downstream_dependents': metrics_row['downstream_dependents'],
                'average_comment_length_7m': metrics_row['average_comment_length_7m'],
                'active_contributor_growth_7m': metrics_row['active_contributor_growth_7m'],
                'time_to_close_issues_7m': metrics_row['time_to_close_issues_7m'],
                'time_first_comment_issues_7m': metrics_row['time_first_comment_issues_7m'],
                'time_to_close_PRs_7m': metrics_row['time_to_close_PRs_7m'],
                'time_first_comment_close_PRs_7m': metrics_row['time_first_comment_close_PRs_7m'],
                'labels': metrics_row['labels'],
                'community_health_percentage': metrics_row['community_health_percentage'],
                'headings_code_of_conduct + headings_contributing + headings_governance': safe_int(metrics_row['headings_code_of_conduct'], 0) + safe_int(metrics_row['headings_contributing'], 0) + safe_int(metrics_row['headings_governance'], 0),
                'headings_README': metrics_row['headings_README'],
                'projects_owned_per_maintainer': metrics_row['projects_owned_per_maintainer'],
                'median_age_other_projects': metrics_row['median_age_other_projects'],
                'dependencies_version_staleness': metrics_row['dependencies_version_staleness'],
                'dependencies_with_vulnerabilities': metrics_row['dependencies_with_vulnerabilities'],
                'workflow_runs': metrics_row['workflow_runs'],
                'contributors_per_code_file': metrics_row['contributors_per_code_file'],
                'files_with_2plus_contributors': metrics_row['files_with_2plus_contributors'],
                'time_since_created': metrics_row['time_since_created'],
                'number_of_versions': metrics_row['number_of_versions'],
                'issue_reporters_7m': metrics_row['issue_reporters_7m'],
                'distinct_contributors_7m': metrics_row['distinct_contributors_7m'],
                'submitted_PRs_7m': metrics_row['submitted_PRs_7m'],
                'commits_pushed_7m': metrics_row['commits_pushed_7m'],
                'issues_closed_percentage': metrics_row['issues_closed_percentage'],
                'PRs_closed_percentage': metrics_row['PRs_closed_percentage'],
                'comments_per_commit_7m': metrics_row['comments_per_commit_7m']
            }

        with open(input_file, mode='r', newline='') as summary_infile:
            summary_reader = csv.DictReader(summary_infile)
            summary_header = summary_reader.fieldnames
            summary_rows = list(summary_reader)

        summary_rows.append(new_row)

        with open(output_file, mode='w', newline='') as summary_outfile:
            summary_writer = csv.DictWriter(summary_outfile, fieldnames=summary_header)
            summary_writer.writeheader()
            summary_writer.writerows(summary_rows)

        print(f"Successfully appended metrics data to summary file and saved as {output_file}")

    except FileNotFoundError:
        print(f"Error: One of the files does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_raw_metrics(owner, repo):
    os.makedirs("../output", exist_ok=True)
    metrics_path = f"../output/{owner}_{repo}_raw_metrics.csv"
    repos_data_path = "../data"
    initialize(metrics_path)
    calculate(owner, repo, metrics_path, repos_data_path)
    merge_files(metrics_path, '../input/other_repos_raw_metrics.csv', '../output/merged_raw_metrics.csv')
