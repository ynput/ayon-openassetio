"""AYON OpenAssetIO addon - server part."""
from ayon_server.addons import BaseServerAddon

from .settings import DEFAULT_VALUES, OpenAssetIOSettings


class OpenAssetIOAddon(BaseServerAddon):
    """Server side of the AYON OpenAssetIO addon."""

    settings_model: type[OpenAssetIOSettings] = OpenAssetIOSettings

    async def get_default_settings(self) -> OpenAssetIOSettings:
        """Return default settings."""
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_VALUES)
