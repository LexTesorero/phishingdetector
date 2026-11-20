import json, joblib, numpy as np
from collections import defaultdict
import xgb_compat; xgb_compat.install()

b = joblib.load("models/E4_cost_sensitive_M8_FullStack.joblib")
F = b["features"]

th = defaultdict(list)
for tree in b["xgb"].get_booster().get_dump(dump_format="json"):
    stack = [json.loads(tree)]
    while stack:
        n = stack.pop()
        if "split" in n:
            name = n["split"]
            if name.startswith("f") and name[1:].isdigit(): name = F[int(name[1:])]
            th[name].append(n["split_condition"]); stack.extend(n.get("children", []))

print("XGB split thresholds per feature")
for f in F:
    a = np.array(th[f]) if th[f] else np.array([np.nan])
    print(f"{f:24} n={len(th[f]):5} min={a.min():>14.3f} median={np.median(a):>14.3f} max={a.max():>14.3f}")

rf = b["rf"]
print("\nRF imputer medians:", dict(zip(F, rf.named_steps["simpleimputer"].statistics_)))