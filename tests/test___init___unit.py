"""Unit tests for plugin."""

from __future__ import annotations

import ast

import pytest

from flake8_docstrings_complete import Plugin, DOCSTR_MISSING_FUNC_MSG


def _result(code: str, filename: str = "test_.py") -> tuple[str, ...]:
    """Generate linting results.
    Args:
        code: The code to check.
    Returns:
        The linting result.
    """
    tree = ast.parse(code)
    plugin = Plugin(tree, filename)
    return tuple(f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run())


@pytest.mark.parametrize(
    "code, expected_result",
    [
        pytest.param("", (), id="trivial"),
        pytest.param(
            """
def function_1():
    return
""",
            (f"2:0 {DOCSTR_MISSING_FUNC_MSG}",),
            id="function docstring missing return",
        ),
        pytest.param(
            """
def function_1():
    pass
""",
            (f"2:0 {DOCSTR_MISSING_FUNC_MSG}",),
            id="function docstring missing expression not constant",
        ),
        pytest.param(
            """
def function_1():
    1
""",
            (f"2:0 {DOCSTR_MISSING_FUNC_MSG}",),
            id="function docstring missing expression constnant not string",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
''',
            (),
            id="function docstring",
        ),
    ],
)
def test_plugin_invalid(code: str, expected_result: tuple[str, ...]):
    """
    given: code
    when: linting is run on the code
    then: the expected result is returned
    """
    assert _result(code) == expected_result
