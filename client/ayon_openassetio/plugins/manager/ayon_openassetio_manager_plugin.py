"""Expose AYON manager plugin to the OpenAssetIO plugin system.

'OPENASSETIO_PLUGIN_PATH' points to this directory. The actual plugin
lives in 'ayon_openassetio_manager' package which is on 'PYTHONPATH'.
"""
from ayon_openassetio_manager import openassetioPlugin  # noqa: F401
