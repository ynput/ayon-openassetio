"""Settings of the AYON OpenAssetIO addon."""
from ayon_server.settings import BaseSettingsModel, SettingsField


def _logging_severity_enum() -> list[dict[str, str]]:
    return [
        {"label": "Host default", "value": ""},
        {"label": "Debug API", "value": "0"},
        {"label": "Debug", "value": "1"},
        {"label": "Info", "value": "2"},
        {"label": "Progress", "value": "3"},
        {"label": "Warning", "value": "4"},
        {"label": "Error", "value": "5"},
        {"label": "Critical", "value": "6"},
    ]


class OpenAssetIOSettings(BaseSettingsModel):
    """OpenAssetIO integration settings."""

    enabled: bool = SettingsField(
        True,
        title="Enabled",
        description=(
            "Register AYON as OpenAssetIO manager in launched applications."
        ),
    )
    host_names: list[str] = SettingsField(
        default_factory=list,
        title="Host names",
        description=(
            "AYON host names (e.g. 'nuke') for which OpenAssetIO is set up."
            " Empty list means all applications."
        ),
    )
    use_ui_delegate: bool = SettingsField(
        True,
        title="Register UI delegate",
        description="Register AYON OpenAssetIO UI delegate plugin.",
    )
    override_default_config: bool = SettingsField(
        True,
        title="Override OPENASSETIO_DEFAULT_CONFIG",
        description=(
            "Replace OPENASSETIO_DEFAULT_CONFIG if already set in the"
            " application environment."
        ),
    )
    replace_loaded_paths: bool = SettingsField(
        False,
        title="Load as entity URI",
        description=(
            "Replace file paths put into the scene by loaders with AYON"
            " entity URI, so the host resolves them through OpenAssetIO."
            " Supported hosts: nuke."
        ),
    )
    logging_severity: str = SettingsField(
        "",
        title="Logging severity",
        enum_resolver=_logging_severity_enum,
        description="Value of OPENASSETIO_LOGGING_SEVERITY.",
    )


DEFAULT_VALUES = {
    "enabled": True,
    "host_names": ["nuke"],
    "use_ui_delegate": True,
    "override_default_config": True,
    "replace_loaded_paths": False,
    "logging_severity": "",
}
