import sys
from datetime import datetime, timezone

import pandas as pd

import features as F

df = pd.read_csv(sys.argv[1], low_memory=False)

URLS = [
    "https://www.recipes.wikia.com/wiki/Czech_Cuisine",
    "https://dfykj.blogspot.com/",
    "https://sheer-pirate-0855.typedream.app/",
    "http://divestinvest.org/philanthropy/",
]
COLS = ["qty_nameservers", "is_spf_domain", "time_domain_activation"]


def as_date(v):
    try:
        if v is None or v != v or v < 0:
            return "missing"
        return datetime.fromtimestamp(v, tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return str(v)


for u in URLS:
    print("\n" + u)
    row = df[df.url == u]
    csv = {c: row.iloc[0][c] for c in COLS} if not row.empty else None
    live = F.extract_features(u)
    for c in COLS:
        c_val = csv[c] if csv else "not in CSV"
        l_val = live[c]
        extra = ""
        if c == "time_domain_activation":
            extra = f"   csv={as_date(c_val) if csv else '-'}  live={as_date(l_val)}"
        print(f"  {c:24} csv={c_val!s:>14}  live={l_val!s:>14}{extra}")