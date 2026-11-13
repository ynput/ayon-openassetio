# AYON OpenAssetIO

AYON addon that makes the
[AYON OpenAssetIO manager plugin](https://github.com/ynput/ayon-openassetio-manager-plugin)
available in applications launched through AYON. The plugin is included as a
git submodule and shipped with the addon client code; its Python dependencies
are declared in `client/pyproject.toml`, so they are part of the AYON
dependency package.

## What it does

A pre-launch hook (`client/ayon_openassetio/hooks/pre_openassetio.py`) sets up
the application environment:

| Variable | Value |
| --- | --- |
| `PYTHONPATH` | appends the directory containing `ayon_openassetio_manager` |
| `OPENASSETIO_PLUGIN_PATH` | prepends `plugins/manager` (shim exposing the manager plugin) |
| `OPENASSETIO_UI_PLUGIN_PATH` | prepends `plugins/ui` (shim exposing the UI delegate), optional |
| `OPENASSETIO_DEFAULT_CONFIG` | `resources/openassetio_config.toml` selecting the AYON manager |
| `OPENASSETIO_LOGGING_SEVERITY` | optional, from settings |

`AYON_SERVER_URL`, `AYON_API_KEY` and `AYON_BUNDLE_NAME`, which the manager
reads, are already set by the AYON launcher.

`openassetio` and `openassetio-mediacreation` are **not** distributed by the
addon. They are compiled against the host (e.g. Nuke 15+ ships its own build)
and must come from the host's Python environment.

The same environment can be produced outside of application launch with
`ayon_openassetio.get_openassetio_environment()`.

## Settings

- **Enabled** - turn the integration on/off (per project).
- **Host names** - AYON host names to set up (default `nuke`); empty means all.
- **Register UI delegate** - also register the UI delegate plugin.
- **Override OPENASSETIO_DEFAULT_CONFIG** - replace an existing config path.
- **Load as entity URI** - loaders put an AYON entity URI
  (`ayon+entity://project/folder?product=..&version=v001&representation=..`,
  version padded per project anatomy)
  into the scene instead of the file path, so OpenAssetIO resolves it.
  Implemented as a `LoaderHookPlugin` registered on host install, so host
  integrations stay untouched. After `load`/`update`, file values pointing into
  the loaded representation's publish directory are replaced. Supported hosts:
  `nuke` (add adapters to `HOST_ADAPTERS` in `load_hook.py`).
- **Logging severity** - `OPENASSETIO_LOGGING_SEVERITY` for the host.

## Development

```shell
git clone --recurse-submodules https://github.com/ynput/ayon-openassetio.git
# or, in an existing clone
git submodule update --init --recursive
```

Create the addon package (`package/openassetio-<version>.zip`) with:

```shell
python create_package.py
```

Only the `plugin/` directory and `LICENSE` from the submodule are packaged.
