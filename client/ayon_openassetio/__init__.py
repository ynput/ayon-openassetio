"""AYON OpenAssetIO addon."""
from .addon import (
    OPENASSETIO_ADDON_ROOT,
    OpenAssetIOAddon,
    get_openassetio_environment,
)
from .version import __version__

__all__ = (
    "OPENASSETIO_ADDON_ROOT",
    "OpenAssetIOAddon",
    "__version__",
    "get_openassetio_environment",
)
