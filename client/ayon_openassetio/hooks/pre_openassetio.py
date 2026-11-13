"""Set up OpenAssetIO environment for launched applications."""
from __future__ import annotations

import os
from typing import ClassVar

from ayon_applications import LaunchTypes, PreLaunchHook
from ayon_core.settings import get_project_settings
from ayon_openassetio import get_openassetio_environment

# AYON connection variables required by the manager plugin.
REQUIRED_AYON_ENV_KEYS = (
    "AYON_SERVER_URL",
    "AYON_API_KEY",
    "AYON_BUNDLE_NAME",
)


class OpenAssetIOPrelaunchHook(PreLaunchHook):
    """Register AYON OpenAssetIO manager plugin in launched application."""

    order = 15
    launch_types: ClassVar[set[str]] = {
        LaunchTypes.local,
        LaunchTypes.farm_render,
        LaunchTypes.farm_publish,
    }

    def execute(self) -> None:
        """Fill launch environment based on addon settings."""
        settings = self._get_addon_settings()
        if not settings.get("enabled", True):
            self.log.debug("OpenAssetIO integration is disabled.")
            return

        host_names = settings.get("host_names") or []
        host_name = self.launch_context.host_name
        if host_names and host_name not in host_names:
            self.log.debug(
                "Skipping OpenAssetIO setup for host '%s'.", host_name
            )
            return

        env = self.launch_context.env
        for key in REQUIRED_AYON_ENV_KEYS:
            if not env.get(key) and os.environ.get(key):
                env[key] = os.environ[key]

        get_openassetio_environment(
            env,
            use_ui_delegate=settings.get("use_ui_delegate", True),
            override_default_config=settings.get(
                "override_default_config", True
            ),
            logging_severity=settings.get("logging_severity", ""),
        )
        self.log.info("AYON OpenAssetIO manager registered.")

    def _get_addon_settings(self) -> dict:
        project_settings = self.data.get("project_settings")
        if project_settings is None:
            project_settings = get_project_settings(
                self.data["project_name"]
            )
        return project_settings.get("openassetio") or {}
