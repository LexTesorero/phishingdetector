"""Extract the 8 X-PHIDE features from a URL."""
import re
from datetime import datetime, timezone
from functools import lru_cache
from urllib.parse import urlparse

import dns.resolver
import tldextract
import whois

FEATURE_ORDER = [
    "length_url",
    "qty_hyphen_path",
    "has_brand_keyword",
    "subdomain_auth_count",
    "qty_nameservers",
    "qty_dot_url",
    "is_spf_domain",
    "time_domain_activation",
]

# TODO: replace with the capsule's lists (verify_features.py helps find them).
BRAND_KEYWORDS = [
    "paypal", "apple", "google", "microsoft", "amazon", "facebook", "netflix",
    "allegrolokalnie",
]
AUTH_KEYWORDS = [
    "login", "signin", "secure", "account", "verify",
    "auth", "password",
]

# Set these from inspect_models.py / verify_features.py output.
MISSING = -1.0            # float("nan") if the models have no negative splits
TIME_DIVISOR = 86400.0    # 1.0 if time_domain_activation thresholds are in seconds
LOOKUP_ON = "registrable" # or "host"

_extract = tldextract.TLDExtract(suffix_list_urls=())  # offline, bundled list
_resolver = dns.resolver.Resolver(configure=False)
_resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
_resolver.lifetime = 5.0
_resolver.timeout = 5.0


def _parse(url: str):
    parsed = urlparse(url if "://" in url else "http://" + url)
    ext = _extract(parsed.netloc)
    return parsed, ext


@lru_cache(maxsize=2048)
def _ns_count(name: str) -> float:
    try:
        return len(_resolver.resolve(name, "NS"))
    except dns.resolver.NoAnswer:
        return 0
    except Exception:
        return MISSING


@lru_cache(maxsize=2048)
def _spf_flag(name: str) -> float:
    try:
        txt = _resolver.resolve(name, "TXT")
        return int(any("v=spf1" in r.to_text().lower() for r in txt))
    except dns.resolver.NoAnswer:
        return 0
    except Exception:
        return MISSING

def _rdap_created(domain: str):
    import json
    import urllib.request

    try:
        with urllib.request.urlopen(f"https://rdap.org/domain/{domain}", timeout=8) as r:
            data = json.load(r)
        for ev in data.get("events", []):
            if ev.get("eventAction") == "registration":
                return datetime.fromisoformat(ev["eventDate"].replace("Z", "+00:00"))
    except Exception:
        pass
    return None


@lru_cache(maxsize=2048)
def _domain_age_seconds(domain: str) -> float:
    # Despite the name, the dataset stores the creation date as a Unix timestamp.
    created = None
    for _ in range(2):
        try:
            created = whois.whois(domain).creation_date
            break
        except Exception:
            pass
    if isinstance(created, list):
        created = created[0] if created else None
    if created is None:
        created = _rdap_created(domain)
    if created is None:
        return MISSING
    try:
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return float(created.timestamp())
    except Exception:
        return MISSING

def offline_features(url: str) -> dict:
    parsed, ext = _parse(url)
    low = url.lower()
    host_no_suffix = ".".join(p for p in (ext.subdomain, ext.domain) if p)
    haystack = low.replace(ext.fqdn, host_no_suffix, 1) if ext.fqdn else low
    sub = ext.subdomain.lower()
    return {
        "length_url": len(url),
        "qty_hyphen_path": parsed.path.count("-"),
        "has_brand_keyword": int(any(b in haystack for b in BRAND_KEYWORDS)),
        "subdomain_auth_count": sum(1 for k in AUTH_KEYWORDS if k in sub),
        "qty_dot_url": url.count("."),
    }


def extract_features(url: str) -> dict:
    parsed, ext = _parse(url)
    registrable = ext.top_domain_under_public_suffix or parsed.hostname or ""
    host = ext.fqdn or parsed.hostname or ""
    return {
        **offline_features(url),
        "qty_nameservers": _ns_count(host) if host else MISSING,
        "is_spf_domain": _spf_flag(registrable) if registrable else MISSING,
        "time_domain_activation": (
            _domain_age_seconds(registrable) if registrable else MISSING
        ),
    }


def normalize_url(url: str) -> str:
    """lowercase / remove leading http(s) / remove leading www"""
    u = url.strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    return u