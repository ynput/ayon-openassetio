"""Nuke adapter replacing loaded file paths by AYON entity URIs."""
from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any

import nuke

from ayon_openassetio.load_hook import normalize_path


def _iter_nodes(node: nuke.Node) -> Iterator[nuke.Node]:
    yield node
    if isinstance(node, nuke.Group):
        for child in node.nodes():
            yield from _iter_nodes(child)


def _get_node(target: Any) -> nuke.Node | None:
    """Get node from loader result or container data."""
    if isinstance(target, nuke.Node):
        return target
    if isinstance(target, dict):
        node = target.get("node")
        if node is None and target.get("objectName"):
            node = nuke.toNode(target["objectName"])
        return node
    return None


def replace_paths(target: Any, published_dir: str, uri: str) -> int:
    """Replace file knob values pointing into published directory.

    Args:
        target (Any): Node returned by loader or container data.
        published_dir (str): Normalized directory of loaded representation.
        uri (str): Entity URI used instead of the path.

    Returns:
        int: Number of replaced knob values.

    """
    node = _get_node(target)
    if node is None:
        return 0

    count = 0
    for item in _iter_nodes(node):
        for knob in item.knobs().values():
            if not isinstance(knob, nuke.File_Knob):
                continue
            value = knob.value()
            if not value or value == uri:
                continue
            if normalize_path(os.path.dirname(value)) != published_dir:
                continue
            knob.setValue(uri)
            count += 1
    return count
