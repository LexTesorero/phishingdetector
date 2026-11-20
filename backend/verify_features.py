# verify_features.py
import sys, re, numpy as np, pandas as pd
from collections import Counter
import features as F

df = pd.read_csv(sys.argv[1], low_memory=False).sample(20000, random_state=0)
off = pd.DataFrame([F.offline_features(u) for u in df.url], index=df.index)

print("Offline feature agreement with the CSV")
for c in off.columns:
    ok = np.isclose(off[c], df[c])
    print(f"  {c:22} {ok.mean():.3f}")
    if ok.mean() < 1:
        print(df.loc[~ok, ["url", c]].head(5).assign(mine=off.loc[~ok, c]).to_string(index=False))

# Candidate brand keywords: tokens present only in rows flagged has_brand_keyword=1
tok = lambda u: set(re.findall(r"[a-z0-9]+", u.lower()))
pos, neg = Counter(), Counter()
for u, f in zip(df.url, df.has_brand_keyword): (pos if f == 1 else neg).update(tok(u))
print("\nTokens only in flagged rows:",
      sorted([(t, c) for t, c in pos.items() if neg[t] == 0 and c >= 5], key=lambda x: -x[1])[:60])

# Host vs registrable lookup: do subdomained URLs fail DNS features more often?
sub = df.url.map(lambda u: F._parse(u)[1].subdomain not in ("", "www"))
for c in ["qty_nameservers", "is_spf_domain", "time_domain_activation"]:
    lo = df[c].min()
    print(f"{c:24} missing-ish rate: subdomain={ (df.loc[sub,c]==lo).mean():.3f}  no-subdomain={ (df.loc[~sub,c]==lo).mean():.3f}")