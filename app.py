from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent / "app"
SPEC = importlib.util.spec_from_file_location(
    "webapp",
    PACKAGE_ROOT / "__init__.py",
    submodule_search_locations=[str(PACKAGE_ROOT)],
)

if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load application package.")

WEBAPP = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = WEBAPP
SPEC.loader.exec_module(WEBAPP)

app = WEBAPP.create_app()


if __name__ == "__main__":
    app.run()