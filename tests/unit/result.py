"""Get the linting result."""

from __future__ import annotations

import ast

from flake8_docstrings_complete import Plugin


def get(code: str, filename: str = "source.py") -> tuple[str, ...]:
    """Generate linting results.

    Args:
        code: The code to check.
        filename: The name of the file the code is in.

    Returns:
        The linting result.
    """
    tree = ast.parse(code)
    plugin = Plugin(tree, filename)
    return tuple(f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run())
