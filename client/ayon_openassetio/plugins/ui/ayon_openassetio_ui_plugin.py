"""Expose AYON UI delegate plugin to the OpenAssetIO plugin system.

'OPENASSETIO_UI_PLUGIN_PATH' points to this directory. The actual plugin
lives in 'ayon_openassetio_manager.ui' package which is on 'PYTHONPATH'.
"""
from ayon_openassetio_manager.ui import openassetioUIPlugin  # noqa: F401
