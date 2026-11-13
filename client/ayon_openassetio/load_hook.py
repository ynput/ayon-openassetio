"""Loader hook replacing loaded file paths by AYON entity URIs.

Loaders of host integrations put resolved file paths into the scene (e.g.
'file' knob of Nuke Read node). In OpenAssetIO enabled hosts the path can be
replaced by AYON entity reference, so the host resolves it through the AYON
OpenAssetIO manager.

The replacement happens in 'post_load' and 'post_update' of
'LoaderHookPlugin', so host integrations don't need to be modified. Each host
needs an adapter that knows where the loaded paths are stored, see
'HOST_ADAPTERS'.
"""
from __future__ import annotations

import importlib
import os
from typing import Any, Callable
from urllib.parse import urlencode

from ayon_core.lib import Logger
from ayon_core.pipeline import Anatomy
from ayon_core.pipeline.load import (
    LoaderPlugin,
    ProductLoaderPlugin,
    get_representation_path_from_context,
)
from ayon_core.pipeline.load.plugins import LoaderHookPlugin

ENTITY_URI_SCHEME = "ayon+entity"

# Host name -> module with 'replace_paths(result, published_dir, uri)'.
#   'result' is return value of loader's 'load' or 'container' passed to
#   'update'. Function returns number of replaced paths.
HOST_ADAPTERS = {
    "nuke": "ayon_openassetio.hosts.nuke",
}

log = Logger.get_logger(__name__)


def get_host_adapter(
    host_name: str | None,
) -> Callable[[Any, str, str], int] | None:
    """Get function replacing paths for the host.

    Args:
        host_name (Optional[str]): AYON host name.

    Returns:
        Optional[Callable[[Any, str, str], int]]: 'replace_paths' function
            or None if host is not supported.

    """
    module_name = HOST_ADAPTERS.get(host_name or "")
    if not module_name:
        return None
    module = importlib.import_module(module_name)
    return module.replace_paths


def get_version_padding(project_name: str) -> int:
    """Get version padding from project anatomy.

    Args:
        project_name (str): Project name.

    Returns:
        int: Version padding.

    """
    return Anatomy(project_name).templates_obj.version_padding


def format_version_name(version: int, padding: int) -> str:
    """Format version number as used in entity URI (e.g. 'v001').

    Args:
        version (int): Version number. Negative value means hero version.
        padding (int): Version padding of the project.

    Returns:
        str: Version name.

    """
    if version < 0:
        return "hero"
    return f"v{version:0{padding}d}"


def build_representation_entity_uri(
    context: dict[str, Any], version_padding: int | None = None
) -> str:
    """Build AYON entity URI of representation in load context.

    Args:
        context (dict[str, Any]): Representation context with 'project',
            'folder', 'product', 'version' and 'representation' entities.
        version_padding (int | None): Version padding. Taken from project
            anatomy when not passed.

    Returns:
        str: Entity URI resolvable by AYON OpenAssetIO manager.

    """
    project_name = context["project"]["name"]
    if version_padding is None:
        version_padding = get_version_padding(project_name)
    query = urlencode({
        "product": context["product"]["name"],
        "version": format_version_name(
            context["version"]["version"], version_padding
        ),
        "representation": context["representation"]["name"],
    })
    folder_path = context["folder"]["path"].strip("/")
    return f"{ENTITY_URI_SCHEME}://{project_name}/{folder_path}?{query}"


def normalize_path(path: str) -> str:
    """Normalize path for comparison.

    Args:
        path (str): Path to normalize.

    Returns:
        str: Normalized path.

    """
    return os.path.normcase(os.path.normpath(path.replace("\\", "/")))


class EntityURILoaderHook(LoaderHookPlugin):
    """Replace paths put into scene by loaders with AYON entity URIs."""

    order = 100
    host_name: str | None = None

    @classmethod
    def is_compatible(cls, Loader: type[LoaderPlugin]) -> bool:
        """Product loaders don't load a single representation."""
        return not issubclass(Loader, ProductLoaderPlugin)

    def pre_load(self, *args: Any, **kwargs: Any) -> None:
        pass

    def post_load(
        self,
        plugin: LoaderPlugin,
        result: Any,
        context: dict,
        name: str | None = None,
        namespace: str | None = None,
        options: dict | None = None,
    ) -> None:
        self._replace(plugin, result, context)

    def pre_update(self, *args: Any, **kwargs: Any) -> None:
        pass

    def post_update(
        self,
        plugin: LoaderPlugin,
        result: Any,
        container: dict,
        context: dict,
    ) -> None:
        self._replace(plugin, container, context)

    def pre_remove(self, *args: Any, **kwargs: Any) -> None:
        pass

    def post_remove(self, *args: Any, **kwargs: Any) -> None:
        pass

    def _replace(
        self, plugin: LoaderPlugin, target: Any, context: Any
    ) -> None:
        """Replace paths of loaded representation in target.

        Failures are only logged, loading itself already succeeded.

        """
        if target is None or not isinstance(context, dict):
            return
        if "representation" not in context:
            return

        try:
            replace_paths = get_host_adapter(self.host_name)
            if replace_paths is None:
                return
            path = get_representation_path_from_context(context)
            published_dir = normalize_path(os.path.dirname(path))
            uri = build_representation_entity_uri(context)
            count = replace_paths(target, published_dir, uri)
        except Exception:
            log.warning(
                "Failed to replace loaded paths by entity URI (%s).",
                plugin.__class__.__name__,
                exc_info=True,
            )
            return

        if count:
            log.debug("Replaced %d path(s) by '%s'.", count, uri)
        else:
            log.debug(
                "No path to replace by '%s' found (%s).",
                uri, plugin.__class__.__name__,
            )
