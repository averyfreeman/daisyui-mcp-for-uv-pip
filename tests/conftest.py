"""Pytest process isolation for the project dependency environment."""

from __future__ import annotations

import os
import sys

for _path in tuple(sys.path):
    if "long-running-tasks-plugin" in _path:
        sys.path.remove(_path)
os.environ.pop("PYTHONPATH", None)
