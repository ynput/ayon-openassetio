"""AYON addon wrapping the OpenAssetIO manager plugin."""
from __future__ import annotations

import logging
import os
from typing import Any

from ayon_core.addon import AYONAddon

from .version import __version__

log = logging.getLogger(__name__)

OPENASSETIO_ADDON_ROOT = os.path.dirname(os.path.abspath(__file__))

# Directory containing the 'ayon_openassetio_manager' Python package
#   (git submodule, see '.gitmodules' in the addon repository).
MANAGER_PLUGIN_PYTHONPATH = os.path.join(
    OPENASSETIO_ADDON_ROOT,
    "vendor",
    "ayon-openassetio-manager-plugin",
    "plugin",
)
# Search paths for the OpenAssetIO plugin system. They contain thin shim
#   modules that expose the plugin classes from 'ayon_openassetio_manager'.
MANAGER_PLUGIN_SEARCH_DIR = os.path.join(
    OPENASSETIO_ADDON_ROOT, "plugins", "manager"
)
UI_PLUGIN_SEARCH_DIR = os.path.join(OPENASSETIO_ADDON_ROOT, "plugins", "ui")
DEFAULT_CONFIG_PATH = os.path.join(
    OPENASSETIO_ADDON_ROOT, "resources", "openassetio_config.toml"
)
MANAGER_IDENTIFIER = "io.ynput.ayon.openassetio.manager"


def _append_path(
    env: dict[str, str],
    key: str,
    path: str,
    prepend: bool = False,
    drop_missing: bool = False,
) -> None:
    """Add path to path-list environment variable if not there yet.

    Args:
        env (dict[str, str]): Environment to update.
        key (str): Environment variable name.
        path (str): Path to add.
        prepend (bool): Put the path first instead of last.
        drop_missing (bool): Remove entries pointing to non-existent
            directories. OpenAssetIO plugin system fails on them.

    """
    current = env.get(key) or ""
    paths = [p for p in current.split(os.pathsep) if p]
    if drop_missing:
        missing = [p for p in paths if not os.path.isdir(p)]
        if missing:
            log.warning(
                "Removing non-existent paths from %s: %s",
                key, ", ".join(missing),
            )
            paths = [p for p in paths if p not in missing]
    normalized = {os.path.normpath(p) for p in paths}
    if os.path.normpath(path) in normalized:
        env[key] = os.pathsep.join(paths)
        return
    if prepend:
        paths.insert(0, path)
    else:
        paths.append(path)
    env[key] = os.pathsep.join(paths)


def get_openassetio_environment(
    env: dict[str, str] | None = None,
    *,
    use_ui_delegate: bool = True,
    override_default_config: bool = True,
    logging_severity: str = "",
) -> dict[str, str]:
    """Fill environment so OpenAssetIO hosts can find the AYON manager.

    Connection to AYON server is driven by 'AYON_SERVER_URL',
    'AYON_API_KEY' and 'AYON_BUNDLE_NAME' which are already part of
    environment of processes launched by AYON launcher.

    Args:
        env (dict[str, str] | None): Environment to update in place.
            New dictionary is created when not passed.
        use_ui_delegate (bool): Register also the UI delegate plugin.
        override_default_config (bool): Replace already defined
            'OPENASSETIO_DEFAULT_CONFIG'.
        logging_severity (str): Value for 'OPENASSETIO_LOGGING_SEVERITY'.
            Empty string keeps the current value.

    Returns:
        dict[str, str]: Updated environment.

    """
    if env is None:
        env = {}

    _append_path(env, "PYTHONPATH", MANAGER_PLUGIN_PYTHONPATH)
    _append_path(
        env, "OPENASSETIO_PLUGIN_PATH", MANAGER_PLUGIN_SEARCH_DIR,
        prepend=True, drop_missing=True,
    )
    if use_ui_delegate:
        _append_path(
            env, "OPENASSETIO_UI_PLUGIN_PATH", UI_PLUGIN_SEARCH_DIR,
            prepend=True, drop_missing=True,
        )

    if override_default_config or not env.get("OPENASSETIO_DEFAULT_CONFIG"):
        env["OPENASSETIO_DEFAULT_CONFIG"] = DEFAULT_CONFIG_PATH

    if logging_severity:
        env["OPENASSETIO_LOGGING_SEVERITY"] = str(logging_severity)

    return env


class OpenAssetIOAddon(AYONAddon):
    """Provide AYON as OpenAssetIO manager to launched applications."""

    name = "openassetio"
    version = __version__

    def initialize(self, studio_settings: dict[str, Any]) -> None:
        """Initialize addon."""
        addon_settings = studio_settings.get(self.name) or {}
        self.enabled = addon_settings.get("enabled", True)

    def on_host_install(
        self, host: Any, host_name: str, project_name: str
    ) -> None:
        """Register loader hook replacing loaded paths by entity URIs."""
        if not project_name:
            return
        from ayon_core.settings import get_project_settings

        settings = get_project_settings(project_name).get(self.name) or {}
        if not settings.get("enabled", True):
            return
        if not settings.get("replace_loaded_paths", False):
            return
        host_names = settings.get("host_names") or []
        if host_names and host_name not in host_names:
            return

        from ayon_core.pipeline.load import register_loader_hook_plugin

        from .load_hook import HOST_ADAPTERS, EntityURILoaderHook

        if host_name not in HOST_ADAPTERS:
            log.warning(
                "Replacing loaded paths by entity URI is not supported"
                " in host '%s'.", host_name,
            )
            return
        EntityURILoaderHook.host_name = host_name
        register_loader_hook_plugin(EntityURILoaderHook)
        log.debug("Registered entity URI loader hook for '%s'.", host_name)

    def get_launch_hook_paths(self) -> list[str]:
        """Paths to application launch hooks.

        Returns:
            list[str]: Launch hook directories.

        """
        return [os.path.join(OPENASSETIO_ADDON_ROOT, "hooks")]
