import os

import matplotlib
import numpy as np
import pandas as pd

# Use a non-GUI backend to avoid macOS thread crashes in background workers.
matplotlib.use("Agg")
from matplotlib import pyplot as plt

def generate_histogram(file_path, column, value, owner, repo):
    # print(f"Generating histogram for {column}: {value}")

    os.makedirs("../images", exist_ok=True)
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.figure(figsize=(10, 2.5))
    df = pd.read_csv(file_path, encoding='gbk')
    df_filtered = df[df[column] != 'N/A'].dropna(subset=[column])
    bin_boundaries = np.linspace(0, 10, num=11)
    hist_values, bin_edges = np.histogram(df_filtered[column], bins=bin_boundaries)
    aim = value
    gap = 0.05

    for i, (start, end) in enumerate(zip(bin_boundaries, bin_boundaries[1:])):
        # print(start, end)
        width = end - start - gap
        # print(hist_values)
        height = hist_values[i] / 5
        if start <= aim < end:
            rect = plt.Rectangle((start + gap / 2, 0), width, height, color='#3A5AFF', fill=True, alpha=0.7)
        else:
            rect = plt.Rectangle((start + gap / 2, 0), width, height, color='#8F8F8F', fill=True, alpha=0.7)
        plt.gca().add_patch(rect)

    plt.ylim(0, 100)
    plt.xlim(0, 10)
    plt.xlabel('→ More trustworthy', color='#8F8F8F', fontsize=20, fontweight=100)
    plt.xticks([])
    ax = plt.gca()
    ax.yaxis.set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    if not os.path.exists(f"../images/{owner}_{repo}"):
        os.mkdir(f"../images/{owner}_{repo}")
    save_path = f"../images/{owner}_{repo}/{column}.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.close()


def generate_image(owner, repo, input_file):
    metrics = pd.read_csv(input_file)
    # print(metrics)
    histograms = ['Community Activity and Integrity', 'Maintenance and Goodwill', 'Code Quality']
    row = metrics[(metrics['owner'] == owner) & (metrics['repo'] == repo)].iloc[0]
    # print(row)
    data = [
        float(row['Community Activity and Integrity']),
        float(row['Maintenance and Goodwill']),
        float(row['Code Quality'])
    ]
    for index, column in enumerate(histograms):
        generate_histogram(input_file, column, data[index], owner, repo)
