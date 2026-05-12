import pandas as pd
import numpy as np

from image import generate_image
from normalize import normalize_metrics, prepare_normalized_metrics_for_readme
from ranking import rank_metrics, prepare_ranked_metrics_for_readme


def write_markdown_to_file(file_path, markdown_content):
    with open(file_path, mode='w') as file:
        file.write(markdown_content)


def get_grade(owner, repo, input_score_file):
    df = pd.read_csv(input_score_file)
    df.replace('', np.nan, inplace=True)
    descending_columns = ['time_to_close_issues_7m', 'time_first_comment_issues_7m', 'time_to_close_PRs_7m',
                          'time_first_comment_close_PRs_7m', 'dependencies_version_staleness',
                          'dependencies_with_vulnerabilities']
    for col in descending_columns:
        if col in df.columns:
            df[col] = 10 - df[col]

    for col in descending_columns:
        mean = df[col].mean()
        std_dev = df[col].std()
        df[f'{col}_Z-Score'] = (df[col] - mean) / std_dev
    df['Combined_Z-Score'] = df[[f'{col}_Z-Score' for col in descending_columns]].mean(axis=1)

    def assign_final_grade(z):
        if z > 1.5:
            return 'a'
        elif z > 0.5:
            return 'b'
        elif z > 0.0:
            return 'c'
        elif z > -0.5:
            return 'd'
        else:
            return 'f'

    df['Final_Grade'] = df['Combined_Z-Score'].apply(assign_final_grade)

    return df[(df['owner'] == owner) & (df['repo'] == repo)]['Final_Grade'].iloc[0]


def generate_readme(owner, repo, input_ranking_file, input_score_file, readme_file):

    df = pd.read_csv(input_score_file)

    grade = get_grade(owner, repo, input_score_file)

    metrics = pd.read_csv(input_ranking_file)
    row = metrics[(metrics['owner'] == owner) & (metrics['repo'] == repo)].iloc[0]

    markdown_content = f"""
# {repo}’s SocialTrust Percentiles

Note: This is a forked repo. The original repo is [here](https://github.com/{owner}/{repo}).
The percentile metrics are based on public social signals through GitHub, so lower ratings may be common for smaller or newer repos.
*Data as of January 31, 2024*

<center><img src="../assets/grades/grade_{grade}.svg" width="100px" height="100px"></center>

This grade is based on the percentile rankings of the 3 trust component scores below, which are compared with the top 1000 most-downloaded npm libraries.

<details>
<summary><span style="font-size: 20px;"><strong>Community Activity and Integrity -- </strong>Beats <strong><span style="color: blue;">{float(row['Community Activity and Integrity'])}%</span></strong> Other Repos</summary>
<div>
<div align=center>
  <img src="../images/{owner}_{repo}/Community Activity and Integrity.png" width="500px" height="170px">
</div>
Activity and usage by this project’s consumers and contributors. More people using and contributing to this project increases these metrics.<br><br>
</div>
<table>
  <tr>
    <td>
      <div>
        <strong>Usage Popularity:</strong> Beats <strong>{float(row['Usage Popularity'])}%</strong>
        <p>How much consumers use this project: stars, watches, forks, downstream dependents.</p>
      </div>
      <div>
        <strong>Code Contribution:</strong> Beats <strong>{float(row['Code Contribution'])}%</strong>
        <p>Activity which adds to the codebase: commits and PRs.</p>
      </div>
    </td>
    <td>
      <div>
        <strong>Contributor Participation:</strong> Beats <strong>{float(row['Contributor Participation'])}%</strong>
        <p>Activity in discussion and participation: number of contributors, comments made, quality of comments.</p>
      </div>
      <div>
        <strong>Contributor Growth:</strong> Beats <strong>{float(row['Contributor Growth'])}%</strong>
        <p>How the project is scaling in size: change in contributors, PRs.</p>
      </div>
    </td>
  </tr>
</table>
</details>


<details>
<summary><span style="font-size: 20px;"><strong>Maintenance and Goodwill -- </strong>Beats <strong><span style="color: blue;">{float(row['Maintenance and Goodwill'])}%</span></strong> Other Repos</summary>
<div>
<div align=center>
  <img src="../images/{owner}_{repo}/Maintenance and Goodwill.png" width="500px" height="170px">
</div>
Activity and involvement by this project’s maintainer(s) for the benefit of the project community. Maintainers could increase these metrics by extending documentation and being more responsive to community participation (especially issues and PRs).<br><br>
</div> 
<table>
  <tr>
    <td>
      <div>
        <strong>Issues Maintenance:</strong> Beats <strong>{float(row['Issues Maintenance'])}%</strong>
        <p>How efficiently issues are addressed: issues closed and comments on issues.</p>
      </div>
      <div>
        <strong>Community Documentation:</strong> Beats <strong>{float(row['Community Documentation'])}%</strong>
        <p>Support for the community to participate: issue and PR templates, code of conduct, governance, etc.</p>
      </div>
    </td>
    <td>
      <div>
        <strong>Code Maintenance:</strong> Beats <strong>{float(row['Code Maintenance'])}%</strong>
        <p>How efficiently code changes are addressed: commits and PRs closed, commit standards.</p>
      </div>
      <div>
        <strong>Maintainer History:</strong> Beats <strong>{float(row['Maintainer History'])}%</strong>
        <p>Maintainer experience: maintainers' other projects.</p>
      </div>
    </td>
  </tr>
</table>
</details>


<details>
<summary><span style="font-size: 20px;"><strong>Code Quality -- </strong>Beats <strong><span style="color: blue;">{float(row['Code Quality'])}%</span></strong> Other Repos</summary>
<div>
<div align=center>
  <img src="../images/{owner}_{repo}/Code Quality.png" width="500px" height="170px">
</div>
Security and scalability of the project’s code. Contributors can increase these metrics by maintaining the dependencies and setting up automated testing and procedural reviews.<br><br>
</div> 
<table>
  <tr>
    <td>
      <div>
        <strong>Dependencies Health:</strong> Beats <strong>{float(row['Dependencies Health'])}%</strong>
        <p>Mitigation of dependency vulnerability risk: dependency versions, reported vulnerabilities.</p>
      </div>
      <div>
        <strong>Review Coverage:</strong> Beats <strong>{float(row['Review Coverage'])}%</strong>
        <p>Scale of manual code reviews: contributors and reviewers per code portion, commit sizes.</p>
      </div>
    </td>
    <td>
      <div>
        <strong>Testing Quality:</strong> Beats <strong>{float(row['Testing Quality'])}%</strong>
        <p>Scale of automated tests: workflow runs, check runs, code authors.</p>
      </div>
      <div>
        <strong>Project Maturity:</strong> Beats <strong>{float(row['Project Maturity'])}%</strong>
        <p>Size and age of repo: lines of code, creation time, versions.</p>
      </div>
    </td>
  </tr>
</table>
</details>



***
        """
    write_markdown_to_file(readme_file, markdown_content)
    print(f"Readme.md has been successfully written to {readme_file}")



def get_social_trust_readme_file(owner, repo):
    normalize_metrics('../output/merged_raw_metrics.csv', '../output/normalized_metrics.csv')
    prepare_normalized_metrics_for_readme('../output/normalized_metrics.csv', '../output/readme_normalized_metrics.csv')
    generate_image(owner, repo, '../output/readme_normalized_metrics.csv', )
    rank_metrics('../output/normalized_metrics.csv', '../output/ranked_metrics.csv')
    prepare_ranked_metrics_for_readme('../output/ranked_metrics.csv', '../output/readme_ranked_metrics.csv')
    generate_readme(owner, repo,'../output/readme_ranked_metrics.csv', '../output/normalized_metrics.csv', f'../docs/README_{repo}.md' )
