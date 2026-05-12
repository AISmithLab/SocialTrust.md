import numpy as np
import pandas as pd


def rank_metrics(input_file, output_file):
    df = pd.read_csv(input_file)

    df.replace('', np.nan, inplace=True)

    descending_columns = ['time_to_close_issues_7m', 'time_first_comment_issues_7m', 'time_to_close_PRs_7m',
                          'time_first_comment_close_PRs_7m', 'dependencies_version_staleness',
                          'dependencies_with_vulnerabilities']

    ascending_columns = [col for col in df.columns if col not in descending_columns and col not in ['owner', 'repo']]

    ranking_df = df[['owner', 'repo']].copy()

    for col in ascending_columns:
        min_val = df[col].min() - 1
        ranking_df[col] = df[col].fillna(min_val).rank(ascending=False, method='min').astype(int)

    for col in descending_columns:
        max_val = df[col].max() + 1
        ranking_df[col] = df[col].fillna(max_val).rank(ascending=True, method='min').astype(int)

    ranking_df.to_csv(output_file, index=False)
    ranking_df.to_csv(output_file, index=False)

    print(f"Ranked data has been successfully written to {output_file}")


def prepare_ranked_metrics_for_readme(input_file, output_file):
    df = pd.read_csv(input_file)

    metrics_list = []

    for index, row in df.iterrows():
        metrics = {}
        metrics['repo'] = row['repo']
        metrics['owner'] = row['owner']
        # Community Activity and Integrity
        metrics['Usage Popularity'] = int((row['Stars+watchers'] + row['forks'] + row['downstream_dependents']) / 3)
        metrics['Contributor Participation'] = int((row['distinct_contributors_7m'] + row['issue_reporters_7m'] + row[
            'average_comment_length_7m'] + row['comments_per_commit_7m']) / 4)
        metrics['Code Contribution'] = int((row['submitted_PRs_7m'] + row['commits_pushed_7m']) / 2)
        metrics['Contributor Growth'] = int(row['active_contributor_growth_7m'])
        metrics['Community Activity and Integrity'] = int((metrics['Usage Popularity'] + metrics[
            'Contributor Participation'] + metrics['Code Contribution'] + metrics['Contributor Growth']) / 4)

        # Maintenance and Goodwill
        metrics['Issues Maintenance'] = int(
            (row['issues_closed_percentage'] + row['time_to_close_issues_7m'] + row['time_first_comment_issues_7m']) / 3)
        metrics['Code Maintenance'] = int((row['PRs_closed_percentage'] + row['time_to_close_PRs_7m'] + row[
            'time_first_comment_close_PRs_7m'] + row['commits_pushed_7m'] + row['labels']) / 5)
        metrics['Community Documentation'] = int(
            (row['headings_code_of_conduct + headings_contributing + headings_governance'] + row['headings_README']) / 2)
        metrics['Maintainer History'] = int((row['projects_owned_per_maintainer'] + row['median_age_other_projects']) / 2)
        metrics['Maintenance and Goodwill'] = int((metrics['Issues Maintenance'] + metrics['Code Maintenance'] + metrics[
            'Community Documentation'] + metrics['Maintainer History']) / 4)

        # Code Quality
        metrics['Dependencies Health'] = int(
            (row['dependencies_version_staleness'] + row['dependencies_with_vulnerabilities']) / 2)
        metrics['Testing Quality'] = int((row['workflow_runs'] + row['distinct_contributors_7m']) / 2)
        metrics['Review Coverage'] = int((row['contributors_per_code_file'] + row['files_with_2plus_contributors']) / 2)
        metrics['Project Maturity'] = int((row['number_of_versions'] + row['time_since_created']) / 2)
        metrics['Code Quality'] = int((metrics['Dependencies Health'] + metrics['Testing Quality'] + metrics[
            'Review Coverage'] + metrics['Project Maturity']) / 4)

        metrics_list.append(metrics)

    metrics_df = pd.DataFrame(metrics_list)

    for col in metrics_df.columns[2:]:
        metrics_df[col] = (1000 - metrics_df[col]) / 10

    metrics_df.to_csv(output_file, index=False)

    print(f"Ranked data for Readme has been successfully written to {output_file}")
