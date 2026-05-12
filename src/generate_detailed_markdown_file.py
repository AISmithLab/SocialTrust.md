import csv

# read csv
def read_metrics_from_csv(file_path):
    metrics = {}
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for key, value in row.items():
                if value == '':
                    row[key] = '0'
            metrics = row
    return metrics

def generate_markdown(metrics):
    markdown_content = f"""
# Metrics Detail -- {metrics['repo']}

- **Website Link:** [[link](https://github.com/{metrics['owner']}/{metrics['repo']})]
- *as of 2024.01.31. GitHub Commit History for this file: [[link]](https://github.com/{metrics['owner']}/{metrics['repo']}/commits/master/)*

*This page provides a detailed breakdown of the metrics discussed on the previous page.*

## Community Activity and Integrity

### User Popularity

*Average of normalized below metrics*

- Number of stars and watchers
  - Number of [stars](https://docs.github.com/en/get-started/exploring-projects-on-github/saving-repositories-with-stars#about-stars) : {metrics['stars']}
  - Number of [watchers](https://docs.github.com/en/rest/activity/watching?apiVersion=2022-11-28#about-watching) : {metrics['watchers']}

- Number of [forks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) : {metrics['forks']}
- Number of [downstream dependents](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/exploring-the-dependencies-of-a-repository) : {metrics['downstream_dependents']}

### Contributor Participation

*Average of normalized below metrics*

-  Number of distinct contributors and issue reporters (7 months) 

     - Number of distinct [contributors](https://opensource.guide/how-to-contribute/#anatomy-of-an-open-source-project) (7 months) : {metrics['distinct_contributors_7m']}
     - Number of [issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) reporters (7 months) : {metrics['issue_reporters_7m']}

- Number of comments per [commit](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/about-commits) (7 months) : {metrics['comments_per_commit_7m']}
- Average length of comments (7 months) : {metrics['average_comment_length_7m']}

### Code Contribution

*Average of normalized below metrics*

- Number of submitted [PR](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)s (7 months) : {metrics['submitted_PRs_7m']}
- Number of [commits](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/about-commits) pushed (7 months) : {metrics['commits_pushed_7m']}

### Contributor Growth

*Average of normalized below metrics*

- Change in number of active [contributors](https://opensource.guide/how-to-contribute/#anatomy-of-an-open-source-project) (7 months) : {metrics['active_contributor_growth_7m']} contributors found in last 7 months.


## Maintenance and Goodwill

### Issues Maintenance

*Average of normalized (Normalized for percentage, Inverse normalized for time) below metrics*

- Percentage of [issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) closed : {float(metrics['issues_closed_percentage']) * 100}%
- Average time to close [issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) (7 months) : {metrics['time_to_close_issues_7m']} days
- Average time until first [maintainers](https://opensource.guide/how-to-contribute/#anatomy-of-an-open-source-project) comment on [issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-issues) (7 months) : {metrics['time_first_comment_issues_7m']} days

### Code Maintenance

*Average of normalized (Normalized for percentage and number, Inverse normalized for time and days) below metrics*

- Percentage of [PR](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)s closed : {float(metrics['PRs_closed_percentage']) * 100}%
- Time to close [PR](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)s (7 months) : {metrics['time_to_close_PRs_7m']} days
- Time until first [maintainer](https://opensource.guide/how-to-contribute/#anatomy-of-an-open-source-project) comment or close on [PR](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)s (7 months) : {metrics['time_first_comment_close_PRs_7m']} days
- Number of [commits](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/about-commits) closed (7 months) : {metrics['commits_7m']} days
- Number of [commit](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/about-commits) tags (7 months) : {metrics['labels']}

### Community Documentation

*Average of normalized below metrics*

- [health percentage](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file) : {metrics['community_health_percentage']}
- Number of headings in code of conduct, contributing, governance documents
  - Number of headings (#, ##, ###) in [code of conduct](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-code-of-conduct-to-your-project) : {metrics['headings_code_of_conduct']}
  - Number of headings (#, ##, ###) in [contributing](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors) : {metrics['headings_contributing']}
  - Number of headings (#, ##, ###) in governance documents : {metrics['headings_governance']}
- Number of headings in [README](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) : {metrics['headings_README']}

### Maintainer History

*Average of normalized below metrics*

- Average number of projects owned by each [maintainer](https://opensource.guide/how-to-contribute/#anatomy-of-an-open-source-project) : {metrics['projects_owned_per_maintainer']}
- Median age of other projects owned by each [maintainer](https://opensource.guide/how-to-contribute/#anatomy-of-an-open-source-project) : {metrics['median_age_other_projects']} days

## Code Quality

### Dependencies Health

*Average of normalized (normalized for percentage, inverse normalized for number) below metrics*

- Dependencies version staleness : {metrics['dependencies_version_staleness']}
- Number of  [dependencies](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/exploring-the-dependencies-of-a-repository) : {metrics['number_of_dependencies']}
- Number of [dependencies](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/exploring-the-dependencies-of-a-repository) with unaddressed vulnerabilities : {metrics['dependencies_with_vulnerabilities']}

### Testing Quality

*Average of normalized below metrics*

- Number of [check runs](https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-checks?apiVersion=2022-11-28) : {metrics['check_runs']}
- Number of [workflow](https://docs.github.com/en/actions/using-workflows/about-workflows) runs : {metrics['workflow_runs']}
- Distinct number of perople who closed [PR](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)s (7 months) : {metrics['distinct_people_closed_PRs_7m']}

### Review Coverage

*Average of normalized (normalized for number, inverse normalized for percentage) below metrics*

- Number of [contributors](https://opensource.guide/how-to-contribute/#anatomy-of-an-open-source-project) per code file : {metrics['contributors_per_code_file']}
- Percentage of files with 2+ contributors : {metrics['files_with_2plus_contributors']}

### Project Maturity

*Average of below normalized metrics*

- Time since created : {metrics['time_since_created']} days
- Number of [versions](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) : {metrics['number_of_versions']}
    """
    return markdown_content


def write_markdown_to_file(file_path, markdown_content):
    with open(file_path, mode='w') as file:
        file.write(markdown_content)
    print(f"Successfully generated detailed markdown file and saved as {file_path}")

def get_detailed_markdown_file(owner, repo):
    metrics_path = f"../output/{owner}_{repo}_raw_metrics.csv"
    markdown_file_path = f"../docs/Metrics_detail_template_Component_(Integrity)_{repo}.md"
    metrics = read_metrics_from_csv(metrics_path)
    markdown_content = generate_markdown(metrics)
    write_markdown_to_file(markdown_file_path, markdown_content)
