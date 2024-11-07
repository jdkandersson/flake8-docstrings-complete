"""Unit tests for args checks in the plugin."""

from __future__ import annotations

import pytest

from flake8_docstrings_complete.args import (
    ARG_IN_DOCSTR_MSG,
    ARG_NOT_IN_DOCSTR_MSG,
    ARGS_SECTION_IN_DOCSTR_MSG,
    ARGS_SECTION_NOT_IN_DOCSTR_MSG,
    DUPLICATE_ARG_MSG,
    MULT_ARGS_SECTIONS_IN_DOCSTR_MSG,
)

from . import result


@pytest.mark.parametrize(
    "code, expected_result",
    [
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
def function_1(arg_1):
    """Docstring 1."""

def function_2(arg_2):
    """Docstring 2."""
''',
            (
                f"3:4 {ARGS_SECTION_NOT_IN_DOCSTR_MSG}",
                f"6:4 {ARGS_SECTION_NOT_IN_DOCSTR_MSG}",
            ),
            id="multiple function has single arg docstring no args section",
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
def _function_1():
    """Docstring 1.

    Args:
    """
''',
            (f"3:4 {ARGS_SECTION_IN_DOCSTR_MSG}",),
            id="private function has no args docstring args section",
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
            (f"3:4 {MULT_ARGS_SECTIONS_IN_DOCSTR_MSG % 'Args,Args'}",),
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
            (f"3:4 {MULT_ARGS_SECTIONS_IN_DOCSTR_MSG % 'Args,Arguments'}",),
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
def function_1(_arg_1):
    """Docstring 1.

    Args:
    """
''',
            (f"3:4 {ARGS_SECTION_IN_DOCSTR_MSG}",),
            id="function has single unused arg docstring args",
        ),
        pytest.param(
            '''
async def function_1(arg_1):
    """Docstring 1.

    Args:
    """
''',
            (f"2:21 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="async function has single arg docstring no arg",
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
    """Docstring."""
    def function_1(self, arg_1, /):
        """Docstring 1.

        Args:
        """
''',
            (f"4:25 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
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
    """Docstring."""
    def function_1(self, *, arg_1):
        """Docstring 1.

        Args:
        """
''',
            (f"4:28 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
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
def function_1(_arg_1, arg_2):
    """Docstring 1.

    Args:
    """
        ''',
            (f"2:23 {ARG_NOT_IN_DOCSTR_MSG % 'arg_2'}",),
            id="function multiple args first unused docstring no arg",
        ),
        pytest.param(
            '''
def function_1(arg_1, _arg_2):
    """Docstring 1.

    Args:
    """
        ''',
            (f"2:15 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="function multiple args second unused docstring no arg",
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
def function_1(arg_1):
    """Docstring 1.

    Args:
        arg_1:
        arg_1:
    """
''',
            (f"3:4 {DUPLICATE_ARG_MSG % 'arg_1'}",),
            id="function single arg docstring duplicate arg",
        ),
        pytest.param(
            '''
def function_1(_arg_1):
    """Docstring 1.

    Args:
        _arg_1:
        _arg_1:
    """
''',
            (f"3:4 {DUPLICATE_ARG_MSG % '_arg_1'}",),
            id="function single unused arg docstring duplicate arg",
        ),
        pytest.param(
            '''
def function_1(arg_1):
    """Docstring 1.

    Args:
        arg_1:
        arg_1:
        arg_1:
    """
''',
            (f"3:4 {DUPLICATE_ARG_MSG % 'arg_1'}",),
            id="function single arg docstring duplicate arg many",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1.

    Args:
        arg_1:
        arg_1:
        arg_2:
    """
''',
            (f"3:4 {DUPLICATE_ARG_MSG % 'arg_1'}",),
            id="function multiple arg docstring duplicate arg first",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1.

    Args:
        arg_1:
        arg_2:
        arg_2:
    """
''',
            (f"3:4 {DUPLICATE_ARG_MSG % 'arg_2'}",),
            id="function multiple arg docstring duplicate arg second",
        ),
        pytest.param(
            '''
def function_1(arg_1, arg_2):
    """Docstring 1.

    Args:
        arg_1:
        arg_1:
        arg_2:
        arg_2:
    """
''',
            (f"3:4 {DUPLICATE_ARG_MSG % 'arg_1'}", f"3:4 {DUPLICATE_ARG_MSG % 'arg_2'}"),
            id="function multiple arg docstring duplicate arg all",
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
def _function_1(arg_1):
    """Docstring 1.

    Args:
        arg_1:
    """
''',
            (),
            id="private function single arg docstring single arg",
        ),
        pytest.param(
            '''
def function_1(_arg_1):
    """Docstring 1.

    Args:
        _arg_1:
    """
''',
            (),
            id="function single unused arg docstring single arg",
        ),
        pytest.param(
            '''
def _function_1(arg_1):
    """Docstring 1."""
''',
            (),
            id="private function single arg docstring no arg",
        ),
        pytest.param(
            '''
def function_1(_arg_1):
    """Docstring 1."""
''',
            (),
            id="function single unused arg docstring no args",
        ),
        pytest.param(
            '''
def function_1(*_args):
    """Docstring 1.

    Args:
        _args:
    """
''',
            (),
            id="function single unused *args docstring single arg",
        ),
        pytest.param(
            '''
def function_1(*_args):
    """Docstring 1."""
''',
            (),
            id="function single unused *args docstring no args",
        ),
        pytest.param(
            '''
def function_1(**_kwargs):
    """Docstring 1.

    Args:
        _kwargs:
    """
''',
            (),
            id="function single unused **kwargs docstring single arg",
        ),
        pytest.param(
            '''
def function_1(**_kwargs):
    """Docstring 1."""
''',
            (),
            id="function single unused **kwargs docstring no args",
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
            '''
def function_1(_arg_1, arg_2):
    """Docstring 1.

    Args:
        arg_2:
    """
''',
            (),
            id="function multiple arg first unused docstring single arg",
        ),
        pytest.param(
            '''
def function_1(arg_1, _arg_2):
    """Docstring 1.

    Args:
        arg_1:
    """
''',
            (),
            id="function multiple arg first unused docstring single arg",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1(self, arg_1):
        """Docstring 1."""
''',
            (f"5:8 {ARGS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="method has single arg docstring no args section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1(self):
        """Docstring 1.

        Args:
        """
''',
            (f"5:8 {ARGS_SECTION_IN_DOCSTR_MSG}",),
            id="method has no args docstring args section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1(self, arg_1):
        """Docstring 1.

        Args:
        """
''',
            (f"4:25 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="method has single arg docstring no arg",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    @staticmethod
    def function_1(arg_1):
        """Docstring 1.

        Args:
        """
''',
            (f"5:19 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="method has single arg docstring no arg staticmethod",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    @classmethod
    def function_1(cls, arg_1):
        """Docstring 1.

        Args:
        """
''',
            (f"5:24 {ARG_NOT_IN_DOCSTR_MSG % 'arg_1'}",),
            id="method has single arg docstring no arg classmethod",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1(self, arg_1):
        """Docstring 1.

        Args:
            arg_1:
            arg_1:
        """
''',
            (f"5:8 {DUPLICATE_ARG_MSG % 'arg_1'}",),
            id="method single arg docstring single arg duplicate",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
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
class Class1:
    """Docstring."""
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
class Class1:
    """Docstring."""
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
def test_plugin(code: str, expected_result: tuple[str, ...]):
    """
    given: code
    when: linting is run on the code
    then: the expected result is returned
    """
    assert result.get(code) == expected_result
