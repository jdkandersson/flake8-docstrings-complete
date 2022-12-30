"""Unit tests for plugin."""

from __future__ import annotations

import ast

import pytest

from flake8_docstrings_complete import (
    Plugin,
    DOCSTR_MISSING_FUNC_MSG,
    ARG_NOT_IN_DOCSTR_MSG,
    ARGS_SECTION_NOT_IN_DOCSTR_MSG,
)


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
def function_1(arg_1):
    """Docstring 1."""
''',
            (f"3:4 {ARGS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function has single arg docstring no args section",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1."""
''',
            (f"3:4 {ARGS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function has multiple arg docstring no args section",
        ),
        pytest.param(
            '''
def function_1(arg_1):
    """Docstring 1.

    Args:
    """
''',
            (f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1 should be described in the docstring'}",),
            id="function has single arg docstring no arg",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1.

    Args:
    """
        ''',
            (
                f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1 should be described in the docstring'}",
                f"2:22 {ARG_NOT_IN_DOCSTR_MSG % 'arg_2 should be described in the docstring'}",
            ),
            id="function multiple args docstring no arg",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1.

    Args:
        arg_1:
    """
''',
            (f"2:22 {ARG_NOT_IN_DOCSTR_MSG % 'arg_2 should be described in the docstring'}",),
            id="function multiple args docstring single arg first",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1.

    Args:
        arg_2:
    """
''',
            (f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1 should be described in the docstring'}",),
            id="function multiple args docstring single arg second",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
''',
            (),
            id="function docstring",
        ),
        pytest.param(
            '''
def function_1(arg_1):
    """Docstring 1.

    Args:
        arg_1:
    """
''',
            (),
            id="function single arg docstring single arg",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1.

    Args:
        arg_1:
        arg_2:
    """
''',
            (),
            id="function multiple arg docstring multiple arg",
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
