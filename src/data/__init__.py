"""Data layer package initialization."""
from .asset_registry import AssetRegistry, get_default_registry
from .market_data import MarketDataManager, fetch_asset_history
from .storage import StorageManager
