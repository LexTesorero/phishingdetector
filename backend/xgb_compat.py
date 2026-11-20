"""Recover XGBoost Boosters from pickles whose snapshot XGBoost refuses to read.

When Booster.__setstate__ fails, decode the UBJSON snapshot, extract the
portable 'Model' section and load it via load_model(). Call install() BEFORE
joblib.load / pickle.load.
"""
import json
import struct

import xgboost.core as xc

_NUM = {
    "i": (">b", 1), "U": (">B", 1), "I": (">h", 2), "l": (">i", 4),
    "L": (">q", 8), "d": (">f", 4), "D": (">d", 8),
}


class _UBJ:
    def __init__(self, buf: bytes):
        self.b = memoryview(buf)
        self.p = 0

    def _read(self, n):
        s = self.p
        self.p += n
        return self.b[s:self.p]

    def _peek(self):
        return chr(self.b[self.p])

    def _num(self, m):
        fmt, size = _NUM[m]
        return struct.unpack(fmt, self._read(size))[0]

    def _length(self):
        return int(self._num(chr(self._read(1)[0])))

    def _key(self):
        return bytes(self._read(self._length())).decode("utf-8")

    def _header(self):
        typ = count = None
        if self._peek() == "$":
            self.p += 1
            typ = chr(self._read(1)[0])
        if self._peek() == "#":
            self.p += 1
            count = self._length()
        return typ, count

    def value(self, m=None):
        if m is None:
            m = chr(self._read(1)[0])
        if m in _NUM:
            return self._num(m)
        if m == "Z":
            return None
        if m == "T":
            return True
        if m == "F":
            return False
        if m == "C":
            return chr(self._read(1)[0])
        if m == "S":
            return bytes(self._read(self._length())).decode("utf-8")
        if m == "[":
            return self._array()
        if m == "{":
            return self._object()
        raise ValueError(f"Unsupported UBJSON marker {m!r} at byte {self.p}")

    def _array(self):
        typ, count = self._header()
        if count is not None:
            if typ in _NUM:
                fmt, size = _NUM[typ]
                raw = self._read(count * size)
                return list(struct.unpack(f">{count}{fmt[1:]}", raw))
            return [self.value(typ) for _ in range(count)]
        out = []
        while self._peek() != "]":
            if self._peek() == "N":
                self.p += 1
                continue
            out.append(self.value())
        self.p += 1
        return out

    def _object(self):
        typ, count = self._header()
        d = {}
        if count is not None:
            for _ in range(count):
                k = self._key()
                d[k] = self.value(typ)
            return d
        while self._peek() != "}":
            if self._peek() == "N":
                self.p += 1
                continue
            k = self._key()
            d[k] = self.value()
        self.p += 1
        return d


def extract_model(raw: bytes) -> dict:
    decoded = _UBJ(raw).value()
    if isinstance(decoded, dict):
        if "learner" in decoded:
            return decoded
        if isinstance(decoded.get("Model"), dict):
            return decoded["Model"]
    keys = list(decoded.keys()) if isinstance(decoded, dict) else type(decoded)
    raise RuntimeError(f"Could not find the model in the snapshot. Top-level: {keys}")


_installed = False


def install():
    global _installed
    if _installed:
        return
    _orig = xc.Booster.__setstate__

    def _setstate(self, state):
        try:
            _orig(self, state)
            return
        except xc.XGBoostError:
            raw = state.get("handle") if isinstance(state, dict) else None
            if raw is None:
                raise
        model = extract_model(bytes(raw))
        tmp = xc.Booster()
        tmp.load_model(bytearray(json.dumps(model).encode("utf-8")))
        self.__dict__.update({k: v for k, v in state.items() if k != "handle"})
        self.handle = tmp.handle
        tmp.handle = None  # ownership moved to self

    xc.Booster.__setstate__ = _setstate
    _installed = True