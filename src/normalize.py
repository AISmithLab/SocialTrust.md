import csv
import numpy as np
import pandas as pd


def read_csv(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        data = csv.reader(file)
        headers = next(data)
        return [list(row) for row in data], headers


def write_csv(data, headers, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)


def normalize_metrics(input_file, output_file):
    original_data, headers = read_csv(input_file)
    normalized_data = []

    # for index, header in enumerate(headers):
    #     print(index, header)

    descending_columns = ['time_to_close_issues_7m', 'time_first_comment_issues_7m', 'time_to_close_PRs_7m',
                          'time_first_comment_close_PRs_7m', 'dependencies_version_staleness',
                          'dependencies_with_vulnerabilities']

    for col_index in range(len(headers)):
        # print(col_index, headers[col_index])
        column_data = [row[col_index] for row in original_data]
        if col_index > 1:  # except owner and repo
            numeric_data_list = [float(x) for x in column_data if x not in ('', 'N/A')]
            if numeric_data_list:
                min_value = min(numeric_data_list)
                max_value = max(numeric_data_list)
            if min_value is None or max_value is None:
                scaled_column = [x for x in column_data]  # 保持原样
            else:
                scaled_column = []
                for x in column_data:
                    if x != '':
                        if headers[col_index] in descending_columns:
                            scaled_column.append(f"{10 - ((float(x) - min_value) / (max_value - min_value)) * 10:.2f}")
                        else:
                            scaled_column.append(f"{(float(x) - min_value) / (max_value - min_value) * 10:.2f}")
                    else:
                        scaled_column.append('')
                normalized_data.append(scaled_column)
        else:
            normalized_data.append(column_data)

    transposed_data = []

    for row in zip(*normalized_data):
        transposed_data.append(list(row))

    write_csv(transposed_data, headers, output_file)

    print(f"Normalized data has been successfully written to {output_file}")


def prepare_normalized_metrics_for_readme(input_file, output_file):
    df = pd.read_csv(input_file)

    df.fillna(0, inplace=True)

    metrics_list = []

    for index, row in df.iterrows():
        metrics = {}
        metrics['repo'] = row['repo']
        metrics['owner'] = row['owner']

        # Community Activity and Integrity
        metrics['Usage Popularity'] = (row['Stars+watchers'] + row['forks'] + row['downstream_dependents']) / 3
        metrics['Contributor Participation'] = (row['distinct_contributors_7m'] + row['issue_reporters_7m'] +
                                                row['average_comment_length_7m'] + row['comments_per_commit_7m']) / 4
        metrics['Code Contribution'] = (row['submitted_PRs_7m'] + row['commits_pushed_7m']) / 2
        metrics['Contributor Growth'] = row['active_contributor_growth_7m']
        metrics['Community Activity and Integrity'] = (metrics['Usage Popularity'] + metrics[
            'Contributor Participation'] + metrics['Code Contribution'] + metrics['Contributor Growth']) / 4

        # Maintenance and Goodwill
        metrics['Issues Maintenance'] = (row['issues_closed_percentage'] + row['time_to_close_issues_7m'] + row[
            'time_first_comment_issues_7m']) / 3
        metrics['Code Maintenance'] = (row['PRs_closed_percentage'] + row['time_to_close_PRs_7m'] + row[
            'time_first_comment_close_PRs_7m'] + row['commits_pushed_7m'] + row['labels']) / 5
        metrics['Community Documentation'] = (row[
                                                  'headings_code_of_conduct + headings_contributing + headings_governance'] +
                                              row['headings_README']) / 2
        metrics['Maintainer History'] = (row['projects_owned_per_maintainer'] + row['median_age_other_projects']) / 2
        metrics['Maintenance and Goodwill'] = (metrics['Issues Maintenance'] + metrics['Code Maintenance'] + metrics[
            'Community Documentation'] + metrics['Maintainer History']) / 4

        # Code Quality
        metrics['Dependencies Health'] = (row['dependencies_version_staleness'] + row[
            'dependencies_with_vulnerabilities']) / 2
        metrics['Testing Quality'] = (row['workflow_runs'] + row['distinct_contributors_7m']) / 2
        metrics['Review Coverage'] = (row['contributors_per_code_file'] + row['files_with_2plus_contributors']) / 2
        metrics['Project Maturity'] = (row['number_of_versions'] + row['time_since_created']) / 2
        metrics['Code Quality'] = (metrics['Dependencies Health'] + metrics['Testing Quality'] + metrics[
            'Review Coverage'] + metrics['Project Maturity']) / 4

        metrics_list.append(metrics)

    metrics_df = pd.DataFrame(metrics_list)

    metrics_df.to_csv(output_file, index=False)

    print(f"Normalized data for Readme has been successfully written to {output_file}")

