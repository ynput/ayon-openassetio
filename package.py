"""AYON OpenAssetIO addon package file."""

name = "openassetio"
title = "OpenAssetIO"
version = "0.1.0+dev"
client_dir = "ayon_openassetio"

services = {}

plugin_for = ["ayon_server"]

ayon_required_addons = {
    "core": ">=1.5.0",
    "applications": ">=1.0.0",
}
ayon_compatible_addons = {}
