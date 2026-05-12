import csv
import os
import time
import psutil
from memory_profiler import memory_usage
import pandas as pd
import numpy as np


from generate_detailed_markdown_file import get_detailed_markdown_file
from generate_social_trust_readme_file import get_social_trust_readme_file
from get_raw_metrics import get_raw_metrics
from scrape import scrape


BASE_DIR = os.path.dirname(__file__)
os.chdir(BASE_DIR)

owner = ""
repo = ""
token = ""

if __name__ == "__main__":

    os.makedirs("../data", exist_ok=True)
    os.makedirs("../output", exist_ok=True)
    os.makedirs("../images", exist_ok=True)
    os.makedirs("../docs", exist_ok=True)

    # 01
    # scrape date for later calculate
    data_dir = f"../data/{owner}_{repo}"
    repo_json_path = os.path.join(data_dir, "repo.json")
    has_cached_data = os.path.isdir(data_dir) and os.listdir(data_dir)
    if os.path.exists(repo_json_path) or has_cached_data:
        print("Using existing data, skipping scrape.")
    else:
        scrape(owner, repo, token)

    # 02
    # calculate raw metrics and saved to '../output'
    # '../output/{owner}_{repo}_raw_metrics.csv' : metrics of target repo
    # '../output/merged_raw_metrics.csv' : metrics combined with other 999 repos
    get_raw_metrics(owner, repo)

    # 03
    # use metrics to generate details.md
    get_detailed_markdown_file(owner, repo)

    # 04
    # use metrics to generate README.md (SocialTrust)
    get_social_trust_readme_file(owner, repo)
