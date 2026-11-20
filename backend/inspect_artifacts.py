import json
from pathlib import Path

import joblib

import xgb_compat

xgb_compat.install()

M = Path(__file__).parent / "models"

print("=== Baseline E0")
base = joblib.load(M / "E0_published_XGB.joblib")
print("  type:", type(base))
if hasattr(base, "get_params"):
    print("  params:", {k: v for k, v in base.get_params().items() if v is not None})
print("  n_features_in_:", getattr(base, "n_features_in_", None))
print("  feature_names:", getattr(base, "feature_names_in_", None))

print("\n=== Stack E4")
b = joblib.load(M / "E4_cost_sensitive_M8_FullStack.joblib")
for k, v in b.items():
    if isinstance(v, (str, int, float, list)):
        print(f"  {k}: {v}")
    else:
        print(f"  {k}: {type(v)}")
print("  xgb booster feature_names:", b["xgb"].get_booster().feature_names)
print("  rf steps:", [type(s).__name__ for _, s in b["rf"].steps])
print("  char_lr steps:", [type(s).__name__ for _, s in b["char_lr"].steps])

vocab = json.loads((M / "E4_CharCNN.vocab.json").read_text(encoding="utf-8"))
v = vocab["vocab"]
print("\n=== vocab.json")
print("  maxlen:", vocab["maxlen"], "| vocab type:", type(v).__name__, "| size:", len(v))
if isinstance(v, dict):
    print("  first 12:", list(v.items())[:12])
else:
    print("  first 12:", v[:12])