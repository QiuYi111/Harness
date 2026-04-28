"""Content-hash computation for cache-engineering support."""

import hashlib
from pathlib import Path


def hash_content(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def fingerprint_layer(paths: list[str], base_dir: Path) -> str:
    """Hash all content in a list of file paths relative to base_dir."""
    hasher = hashlib.sha256()
    for p in sorted(paths):
        fpath = base_dir / p
        if fpath.exists():
            hasher.update(fpath.read_bytes())
    return hasher.hexdigest()[:12]


def fingerprint_layers(layers: dict[str, list[str]], base_dir: Path) -> dict[str, str]:
    """Return {layer_name: hash} for each cache layer."""
    return {name: fingerprint_layer(paths, base_dir) for name, paths in layers.items()}


def load_cache_config(config_path: Path) -> dict:
    """Load cache-context.yaml. Returns layers dict."""
    import yaml

    if config_path.exists():
        data = yaml.safe_load(config_path.read_text())
        return {
            "stable_prefix": data.get("stable_prefix", []),
            "semi_stable_context": data.get("semi_stable_context", []),
            "active_feature_context": data.get("active_feature_context", []),
            "dynamic_suffix": data.get("dynamic_suffix", []),
        }
    return {}


def estimate_tokens(content: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return max(1, len(content) // 4)
