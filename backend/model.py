from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

import xgb_compat

xgb_compat.install()

from features import extract_features, normalize_url  # noqa: E402

MODELS_DIR = Path(__file__).parent / "models"
BASELINE_FILE = "E0_published_XGB.joblib"
STACK_FILE = "E4_cost_sensitive_M8_FullStack.joblib"

MODEL_KEYS = ("baseline", "enhanced")

_state: dict = {}


def load_models():
    _state["baseline"] = joblib.load(MODELS_DIR / BASELINE_FILE)

    bundle = joblib.load(MODELS_DIR / STACK_FILE)
    _state["xgb"] = bundle["xgb"]
    _state["rf"] = bundle["rf"]
    _state["char_lr"] = bundle["char_lr"]
    _state["meta"] = bundle["meta_learner"]
    _state["base_order"] = bundle["base_order"]
    _state["features"] = bundle["features"]
    _state["threshold"] = float(bundle["threshold"])

    import tensorflow as tf  # lazy: slow import

    stem = bundle["cnn_stem"]
    _state["cnn"] = tf.keras.models.load_model(
        MODELS_DIR / f"{stem}.keras", compile=False
    )
    vocab = json.loads((MODELS_DIR / f"{stem}.vocab.json").read_text(encoding="utf-8"))
    _state["vocab"] = vocab["vocab"]
    _state["maxlen"] = int(vocab["maxlen"])


def get_threshold() -> float:
    return _state["threshold"]


def _encode_cnn(texts: list[str]) -> np.ndarray:
    # Matches training: post-pad with 0, truncate to maxlen, unknown char = 1.
    vocab, L = _state["vocab"], _state["maxlen"]
    out = np.zeros((len(texts), L), dtype="int32")
    for i, t in enumerate(texts):
        for j, ch in enumerate(t[:L]):
            out[i, j] = vocab.get(ch, 1)
    return out


def predict(url: str, which: str = "enhanced", feats: dict | None = None) -> float:
    if which not in MODEL_KEYS:
        raise ValueError(f"model must be one of {MODEL_KEYS}")
    if not _state:
        raise NotImplementedError("Models not loaded.")

    cols = _state["features"]
    feats = feats if feats is not None else extract_features(url)
    X = pd.DataFrame([[feats[c] for c in cols]], columns=cols)

    if which == "baseline":
        return float(_state["baseline"].predict_proba(X)[0, 1])

    text = normalize_url(url)
    probs = {
        "xgb": _state["xgb"].predict_proba(X)[:, 1],
        "rf": _state["rf"].predict_proba(X)[:, 1],
        "char_lr": _state["char_lr"].predict_proba([text])[:, 1],
        "cnn": _state["cnn"].predict(_encode_cnn([text]), verbose=0).ravel(),
    }
    Z = np.column_stack([probs[k] for k in _state["base_order"]])
    return float(_state["meta"].predict_proba(Z)[0, 1])