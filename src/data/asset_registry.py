"""
Asset Registry Module.
Manages metadata for supported financial instruments and supports dynamic additions.
"""

from typing import Dict, Any, List, Optional
import config


class AssetRegistry:
    """Registry maintaining metadata for all supported financial instruments."""

    def __init__(self):
        self._assets: Dict[str, Dict[str, Any]] = {}
        self._load_defaults()

    def _load_defaults(self):
        """Populate initial supported assets from config."""
        for label, meta in config.INITIAL_ASSETS.items():
            self._assets[meta["ticker"]] = {
                "label": label,
                "ticker": meta["ticker"],
                "name": meta["name"],
                "category": meta["category"],
                "description": meta["description"],
                "icon": meta.get("icon", "📊"),
                "is_custom": False,
                "currency": "USD"
            }
        
        for label, meta in config.EXTENDED_ASSET_PRESETS.items():
            self._assets[meta["ticker"]] = {
                "label": label,
                "ticker": meta["ticker"],
                "name": meta["name"],
                "category": meta["category"],
                "description": meta["description"],
                "icon": meta.get("icon", "📈"),
                "is_custom": False,
                "currency": "USD"
            }

    def list_assets(self) -> List[Dict[str, Any]]:
        """Return list of all registered asset records."""
        return list(self._assets.values())

    def list_core_assets(self) -> List[Dict[str, Any]]:
        """Return primary core hackathon assets (Gold, Bitcoin, NVIDIA)."""
        core_tickers = ["GLD", "BTC-USD", "NVDA"]
        return [self._assets[t] for t in core_tickers if t in self._assets]

    def get_asset_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a ticker."""
        return self._assets.get(ticker.upper())

    def get_asset(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Alias for get_asset_by_ticker."""
        return self.get_asset_by_ticker(ticker)

    def get_asset_by_label(self, label: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata matching a display label."""
        for meta in self._assets.values():
            if meta["label"] == label:
                return meta
        return None

    def add_custom_asset(
        self, ticker: str, name: str = "", category: str = "Custom Asset", icon: str = "⚡"
    ) -> Dict[str, Any]:
        """Add or update a custom ticker in the registry."""
        cleaned_ticker = ticker.strip().upper()
        if not name:
            name = f"Custom ({cleaned_ticker})"
        label = f"{cleaned_ticker} ({name})"
        
        record = {
            "label": label,
            "ticker": cleaned_ticker,
            "name": name,
            "category": category,
            "description": f"Custom user-added instrument: {cleaned_ticker}",
            "icon": icon,
            "is_custom": True,
            "currency": "USD"
        }
        self._assets[cleaned_ticker] = record
        return record


_global_registry = AssetRegistry()


def get_default_registry() -> AssetRegistry:
    """Return singleton instance of AssetRegistry."""
    return _global_registry
