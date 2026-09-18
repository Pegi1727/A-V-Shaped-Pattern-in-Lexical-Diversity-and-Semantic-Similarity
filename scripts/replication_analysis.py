#!/usr/bin/env python3
"""
Replication Analysis: V-shaped trajectories of lexical, syntactic, cohesion and
semantic metrics across Original -> AI_Revised -> Author_Refined texts (N=30).

Data: data/vshape_30_clean_long.csv (90 rows = 30 participants x 3 stages).
Metrics: MTLD, MLU, Cohesion_Score, SBERT_Similarity.

Usage: python replication_analysis.py
Outputs: figures/vshape_trajectories.png and printed repeated-measures summaries.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "vshape_30_clean_long.csv")
FIGDIR = os.path.join(ROOT, "figures")
METRICS = ["MTLD", "MLU", "Cohesion_Score", "SBERT_Similarity"]
STAGES = ["Original", "AI_Revised", "Author_Refined"]


def load_data():
    df = pd.read_csv(DATA)
    df["Stage"] = pd.Categorical(df["Stage"], categories=STAGES, ordered=True)
    return df


def descriptives(df):
    tab = df.groupby("Stage", observed=True)[METRICS].agg(["mean", "std"]).round(3)
    print("=== Descriptive statistics (mean +/- SD) ===")
    print(tab.to_string())
    return tab


def repeated_measures(df):
    """One-way repeated-measures tests per metric + quadratic (V-shape) contrast."""
    print("\n=== Friedman test and quadratic (V-shaped) contrast ===")
    results = {}
    for m in METRICS:
        wide = df.pivot(index="Participant_ID", columns="Stage", values=m)[STAGES].dropna()
        f, p = stats.friedmanchisquare(*[wide[s] for s in STAGES])
        # quadratic (V-shaped) contrast: Original + Author_Refined - 2*AI_Revised
        contrast = wide["Original"] + wide["Author_Refined"] - 2 * wide["AI_Revised"]
        t, p_q = stats.wilcoxon(contrast)
        results[m] = {"friedman_chi2": round(f, 3), "friedman_p": round(p, 5),
                      "quadratic_W": round(t, 3), "quadratic_p": round(p_q, 5),
                      "quadratic_mean": round(contrast.mean(), 3)}
        print(f"{m}: Friedman chi2={f:.3f}, p={p:.5f} | "
              f"V-contrast mean={contrast.mean():.3f}, Wilcoxon p={p_q:.5f}")
    return results


def plot_trajectories(df, out_path):
    """4-panel plot: individual faint lines + mean +/- 95% CI per metric."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
    x = np.arange(3)
    for ax, m in zip(axes.ravel(), METRICS):
        for pid, g in df.groupby("Participant_ID"):
            ax.plot(x, g.sort_values("Stage")[m], color="grey", alpha=0.25, lw=0.8)
        s = df.groupby("Stage", observed=True)[m].agg(["mean", "std", "count"])
        mean = s["mean"].values
        ci = 1.96 * s["std"].values / np.sqrt(s["count"].values)
        ax.plot(x, mean, "o-", color="crimson", lw=2, label="Mean")
        ax.fill_between(x, mean - ci, mean + ci, color="crimson", alpha=0.2, label="95% CI")
        ax.set_title(m)
        ax.set_xticks(x)
        ax.set_xticklabels(STAGES, rotation=15)
        ax.grid(alpha=0.3)
    axes[0, 0].legend()
    fig.suptitle("V-shaped trajectories across revision stages (N = 30)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, dpi=300)
    print(f"\nFigure saved to {out_path}")


def main():
    df = load_data()
    descriptives(df)
    repeated_measures(df)
    os.makedirs(FIGDIR, exist_ok=True)
    plot_trajectories(df, os.path.join(FIGDIR, "vshape_trajectories.png"))


if __name__ == "__main__":
    main()
