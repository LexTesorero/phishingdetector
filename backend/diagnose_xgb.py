"""Intercept XGBoost Booster bytes during unpickling, report their format,
and try to recover them as portable JSON."""
import pickle
from pathlib import Path

import joblib
import xgboost as xgb
import xgboost.core as xc

print("xgboost version:", xgb.__version__)

M = Path(__file__).parent / "models"
captured = []
_orig = xc.Booster.__setstate__


def _patched(self, state):
    raw = state.get("handle") if isinstance(state, dict) else None
    captured.append(raw)
    try:
        _orig(self, state)
    except Exception as e:
        print(f"  Booster.__setstate__ failed: {type(e).__name__}: {e}")
        self.handle = None  # let unpickling continue so we can inspect the rest


xc.Booster.__setstate__ = _patched

for name in ["E0_published_XGB.pkl", "E4_cost_sensitive_M8_FullStack.pkl"]:
    print(f"\n=== {name}")
    captured.clear()
    with open(M / name, "rb") as f:
        obj = pickle.load(f)
    print("  top-level type:", type(obj))
    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"    {k!r}: {type(v)}")

    for i, raw in enumerate(captured):
        if raw is None:
            print(f"  booster {i}: no raw handle in state")
            continue
        raw = bytes(raw)
        print(f"  booster {i}: {len(raw):,} bytes, head={raw[:16]!r}")
        try:
            b = xgb.Booster()
            b.load_model(bytearray(raw))
            out = M / f"_recovered_{Path(name).stem}_{i}.json"
            b.save_model(str(out))
            print(f"    load_model OK -> saved {out.name}")
        except Exception as e:
            print(f"    load_model FAILED: {type(e).__name__}: {e}")