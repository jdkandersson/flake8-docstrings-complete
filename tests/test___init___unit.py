"""Unit tests for plugin."""

from __future__ import annotations

import ast

import pytest

from flake8_docstrings_complete import (
    ARG_IN_DOCSTR_MSG,
    ARG_NOT_IN_DOCSTR_MSG,
    ARGS_SECTION_IN_DOCSTR_MSG,
    ARGS_SECTION_NOT_IN_DOCSTR_MSG,
    DOCSTR_MISSING_FUNC_MSG,
    MULT_ARGS_SECTION_IN_DOCSTR_MSG,
    Plugin,
)


def _result(code: str, filename: str = "source.py") -> tuple[str, ...]:
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
def function_1():
    """Docstring 1.

    Args:
    """
''',
            (f"3:4 {ARGS_SECTION_IN_DOCSTR_MSG}",),
            id="function has no args docstring args section",
        ),
        pytest.param(
            '''
def function_1(arg_1):
    """Docstring 1.

    Args:
        arg_1:

    Args:
        arg_1:
    """
''',
            (f"3:4 {MULT_ARGS_SECTION_IN_DOCSTR_MSG % 'Args,Args'}",),
            id="function has single args docstring multiple args sections same name",
        ),
        pytest.param(
            '''
def function_1(arg_1):
    """Docstring 1.

    Args:
        arg_1:

    Arguments:
        arg_1:
    """
''',
            (f"3:4 {MULT_ARGS_SECTION_IN_DOCSTR_MSG % 'Args,Arguments'}",),
            id="function has single args docstring multiple args sections different name",
        ),
        pytest.param(
            '''
def function_1(arg_1):
    """Docstring 1.

    Args:
    """
''',
            (f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="function has single arg docstring no arg",
        ),
        pytest.param(
            '''
def function_1(arg_1, /):
    """Docstring 1.

    Args:
    """
''',
            (f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="function has single positional only arg docstring no arg",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2, /):
    """Docstring 1.

    Args:
    """
''',
            (f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}", f"2:22 {ARG_NOT_IN_DOCSTR_MSG % 'arg_2'}"),
            id="function has multiple positional only arg docstring no arg",
        ),
        pytest.param(
            '''
class Class1:
    def function_1(self, arg_1, /):
        """Docstring 1.

        Args:
        """
''',
            (f"3:25 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="method has single positional only arg docstring no arg",
        ),
        pytest.param(
            '''
def function_1(*, arg_1):
    """Docstring 1.

    Args:
    """
''',
            (f"2:18 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="function has single keyword only arg docstring no arg",
        ),
        pytest.param(
            '''
def function_1(*, arg_1, arg_2):
    """Docstring 1.

    Args:
    """
''',
            (f"2:18 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}", f"2:25 {ARG_NOT_IN_DOCSTR_MSG % 'arg_2'}"),
            id="function has multiple keyword only arg docstring no arg",
        ),
        pytest.param(
            '''
class Class1:
    def function_1(self, *, arg_1):
        """Docstring 1.

        Args:
        """
''',
            (f"3:28 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="method has single keyword only arg docstring no arg",
        ),
        pytest.param(
            '''
def function_1(*args):
    """Docstring 1.

    Args:
    """
''',
            (f"2:16 {ARG_NOT_IN_DOCSTR_MSG % 'args'}",),
            id="function has *args docstring no arg",
        ),
        pytest.param(
            '''
def function_1(**kwargs):
    """Docstring 1.

    Args:
    """
''',
            (f"2:17 {ARG_NOT_IN_DOCSTR_MSG % 'kwargs'}",),
            id="function has **kwargs docstring no arg",
        ),
        pytest.param(
            '''
def function_1(*args, **kwargs):
    """Docstring 1.

    Args:
    """
''',
            (
                f"2:16 {ARG_NOT_IN_DOCSTR_MSG % 'args'}",
                f"2:24 {ARG_NOT_IN_DOCSTR_MSG % 'kwargs'}",
            ),
            id="function has *args and **kwargs docstring no arg",
        ),
        pytest.param(
            '''
def function_1(*args, arg_1):
    """Docstring 1.

    Args:
    """
''',
            (f"2:22 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}", f"2:16 {ARG_NOT_IN_DOCSTR_MSG % 'args'}"),
            id="function has *args docstring no arg",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1.

    Args:
    """
        ''',
            (f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}", f"2:22 {ARG_NOT_IN_DOCSTR_MSG % 'arg_2'}"),
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
            (f"2:22 {ARG_NOT_IN_DOCSTR_MSG % 'arg_2'}",),
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
            (f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="function multiple args docstring single arg second",
        ),
        pytest.param(
            '''
def function_1(arg_1):
    """Docstring 1.

    Args:
        arg_2:
    """
''',
            (
                f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",
                f"3:4 {ARG_IN_DOCSTR_MSG % 'arg_2'}",
            ),
            id="function has single arg docstring arg different",
        ),
        pytest.param(
            '''
def function_1(arg_1):
    """Docstring 1.

    Args:
        arg_2:
        arg_3:
    """
        ''',
            (
                f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",
                f"3:4 {ARG_IN_DOCSTR_MSG % 'arg_2'}",
                f"3:4 {ARG_IN_DOCSTR_MSG % 'arg_3'}",
            ),
            id="function single arg docstring multiple args different",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1.

    Args:
        arg_3:
        arg_4:
    """
        ''',
            (
                f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",
                f"2:22 {ARG_NOT_IN_DOCSTR_MSG % 'arg_2'}",
                f"3:4 {ARG_IN_DOCSTR_MSG % 'arg_3'}",
                f"3:4 {ARG_IN_DOCSTR_MSG % 'arg_4'}",
            ),
            id="function multiple arg docstring multiple args different",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1.

    Args:
        arg_3:
        arg_2:
    """
        ''',
            (f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}", f"3:4 {ARG_IN_DOCSTR_MSG % 'arg_3'}"),
            id="function multiple arg docstring multiple args first different",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1.

    Args:
        arg_1:
        arg_3:
    """
        ''',
            (f"2:22 {ARG_NOT_IN_DOCSTR_MSG % 'arg_2'}", f"3:4 {ARG_IN_DOCSTR_MSG % 'arg_3'}"),
            id="function multiple arg docstring multiple args last different",
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
def function_1(*args):
    """Docstring 1.

    Args:
        args:
    """
''',
            (),
            id="function single arg docstring *args",
        ),
        pytest.param(
            '''
def function_1(**kwargs):
    """Docstring 1.

    Args:
        kwargs:
    """
''',
            (),
            id="function single arg docstring **kwargs",
        ),
        pytest.param(
            '''
def function_1(*args, **kwargs):
    """Docstring 1.

    Args:
        args:
        kwargs:
    """
''',
            (),
            id="function single arg docstring *args and **kwargs",
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
        pytest.param(
            """
class Class_1:
    def function_1(self):
        return
""",
            (f"3:4 {DOCSTR_MISSING_FUNC_MSG}",),
            id="method docstring missing return",
        ),
        pytest.param(
            '''
class Class_1:
    def function_1(self, arg_1):
        """Docstring 1."""
''',
            (f"4:8 {ARGS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="method has single arg docstring no args section",
        ),
        pytest.param(
            '''
class Class_1:
    def function_1(self):
        """Docstring 1.

        Args:
        """
''',
            (f"4:8 {ARGS_SECTION_IN_DOCSTR_MSG}",),
            id="method has no args docstring args section",
        ),
        pytest.param(
            '''
class Class_1:
    def function_1(self, arg_1):
        """Docstring 1.

        Args:
        """
''',
            (f"3:25 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="method has single arg docstring no arg",
        ),
        pytest.param(
            '''
class Class_1:
    @staticmethod
    def function_1(arg_1):
        """Docstring 1.

        Args:
        """
''',
            (f"4:19 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="method has single arg docstring no arg staticmethod",
        ),
        pytest.param(
            '''
class Class_1:
    @classmethod
    def function_1(cls, arg_1):
        """Docstring 1.

        Args:
        """
''',
            (f"4:24 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="method has single arg docstring no arg classmethod",
        ),
        pytest.param(
            '''
class Class_1:
    def function_1(self, arg_1):
        """Docstring 1.

        Args:
            arg_1:
        """
''',
            (),
            id="method single arg docstring single arg",
        ),
        pytest.param(
            '''
class Class_1:
    @staticmethod
    def function_1(arg_1):
        """Docstring 1.

        Args:
            arg_1:
        """
''',
            (),
            id="method single arg docstring single arg staticmethod",
        ),
        pytest.param(
            '''
class Class_1:
    @classmethod
    def function_1(cls, arg_1):
        """Docstring 1.

        Args:
            arg_1:
        """
''',
            (),
            id="method single arg docstring single arg classmethod",
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


@pytest.mark.parametrize(
    "code, filename, expected_result",
    [
        pytest.param(
            """
def test_():
    pass
""",
            "source.py",
            (f"2:0 {DOCSTR_MISSING_FUNC_MSG}",),
            id="not test file",
        ),
        pytest.param(
            """
def foo():
    pass
""",
            "test_.py",
            (f"2:0 {DOCSTR_MISSING_FUNC_MSG}",),
            id="test file not test function",
        ),
        pytest.param(
            """
def test_():
    pass
""",
            "test_.py",
            (),
            id="test file test function",
        ),
        pytest.param(
            """
def test_():
    pass
""",
            "tests/test_.py",
            (),
            id="test file test function in directory",
        ),
    ],
)
def test_plugin_filename(code: str, filename: str, expected_result: tuple[str, ...]):
    """
    given: code and filename
    when: linting is run on the code
    then: the expected result is returned
    """
    assert _result(code, filename) == expected_result
