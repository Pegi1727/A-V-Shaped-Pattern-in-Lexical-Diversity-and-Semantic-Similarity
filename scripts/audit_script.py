import pandas as pd, numpy as np
from scipy import stats

df = pd.read_csv('/mnt/data/vshape_30_clean_long.csv')
vars_ = ['MTLD', 'MLU', 'Cohesion_Score', 'SBERT_Similarity']
stages = ['Original', 'AI_Revised', 'Author_Refined']
wide = {v: df.pivot(index='Participant_ID', columns='Stage', values=v)[stages] for v in vars_}
for w in wide.values():
    assert w.notna().all().all() and len(w) == 30

L = []
L.append("# Statistical Audit - vshape_30_clean_long.csv (N = 30)\n")
L.append("Design: one-way repeated measures, 3 stages (Original, AI_Revised, Author_Refined); 30 participants per stage; no missing values.\n")

def desc(x):
    x = np.asarray(x, float)
    return (x.mean(), x.std(ddof=1), x.min(), x.max(),
            np.median(x), np.percentile(x, 75) - np.percentile(x, 25))

for v in vars_:
    L.append("\n## " + v + "\n")
    L.append("| Stage | Mean | SD | Min | Max | Median | IQR |")
    L.append("|---|---|---|---|---|---|---|")
    for s in stages:
        m, sd, mn, mx, md, iq = desc(wide[v][s])
        L.append(f"| {s} | {m:.4f} | {sd:.4f} | {mn:.4f} | {mx:.4f} | {md:.4f} | {iq:.4f} |")
    Y = wide[v]; k, n = 3, 30
    grand = Y.values.mean()
    ss_sub = k * ((Y.mean(axis=1) - grand) ** 2).sum()
    ss_stage = n * ((Y.mean() - grand) ** 2).sum()
    ss_tot = ((Y.values - grand) ** 2).sum()
    ss_err = ss_tot - ss_sub - ss_stage
    df1, df2 = k - 1, (n - 1) * (k - 1)
    F = (ss_stage / df1) / (ss_err / df2)
    p = stats.f.sf(F, df1, df2)
    eta = ss_stage / (ss_stage + ss_err)
    L.append(f"\n**RM-ANOVA**: F({df1}, {df2}) = {F:.4f}, p = {p:.3e}, partial eta^2 = {eta:.4f}\n")
    L.append("| Comparison | Mean Diff | t(29) | p (paired t) | Cohen's dz |")
    L.append("|---|---|---|---|---|")
    for a, b in [('Original', 'AI_Revised'), ('AI_Revised', 'Author_Refined'), ('Original', 'Author_Refined')]:
        d = Y[a].values - Y[b].values
        t, pv = stats.ttest_rel(Y[a].values, Y[b].values)
        L.append(f"| {a} vs {b} | {d.mean():+.4f} | {t:.4f} | {pv:.3e} | {d.mean()/d.std(ddof=1):.4f} |")

holm = []
for v in vars_:
    Y = wide[v]
    for a, b in [('Original', 'AI_Revised'), ('AI_Revised', 'Author_Refined'), ('Original', 'Author_Refined')]:
        t, pv = stats.ttest_rel(Y[a].values, Y[b].values)
        holm.append([v, a, b, t, pv])
ps = np.array([h[4] for h in holm])
adj = np.empty(len(ps)); run = 0.0
for rank, idx in enumerate(np.argsort(ps)):
    run = max(run, ps[idx] * (len(ps) - rank)); adj[idx] = min(run, 1.0)
L.append("\n## Holm-adjusted p-values (12 paired t-tests)\n")
L.append("| Variable | Comparison | t(29) | p raw | p Holm |")
L.append("|---|---|---|---|---|")
for h, pa in zip(holm, adj):
    L.append(f"| {h[0]} | {h[1]} vs {h[2]} | {h[3]:.4f} | {h[4]:.3e} | {pa:.3e} |")

out = '\n'.join(L)
open('/mnt/data/statistical_audit_vshape30.md', 'w').write(out)
print(out)
