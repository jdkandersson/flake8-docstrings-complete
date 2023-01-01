"""Unit tests for plugin."""

# Lines are from many parameters for tests
# pylint:disable=too-many-lines

from __future__ import annotations

import pytest

from flake8_docstrings_complete import (
    ARG_IN_DOCSTR_MSG,
    ARG_NOT_IN_DOCSTR_MSG,
    ARGS_SECTION_IN_DOCSTR_MSG,
    ARGS_SECTION_NOT_IN_DOCSTR_MSG,
    DOCSTR_MISSING_FUNC_MSG,
    MULT_ARGS_SECTION_IN_DOCSTR_MSG,
    MULT_RETURNS_SECTION_IN_DOCSTR_MSG,
    MULT_YIELDS_SECTION_IN_DOCSTR_MSG,
    RETURNS_SECTION_IN_DOCSTR_MSG,
    RETURNS_SECTION_NOT_IN_DOCSTR_MSG,
    YIELDS_SECTION_IN_DOCSTR_MSG,
    YIELDS_SECTION_NOT_IN_DOCSTR_MSG,
)

from . import result


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
    return

def function_2():
    return
""",
            (f"2:0 {DOCSTR_MISSING_FUNC_MSG}", f"5:0 {DOCSTR_MISSING_FUNC_MSG}"),
            id="multiple functions docstring missing return",
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
def function_1(_arg_1):
    """Docstring 1.

    Args:
    """
''',
            (f"3:4 {ARGS_SECTION_IN_DOCSTR_MSG}",),
            id="function has single unused arg docstring no arg",
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
def function_1():
    """Docstring.

    Returns:
    """
''',
            (f"3:4 {RETURNS_SECTION_IN_DOCSTR_MSG}",),
            id="function no return returns in docstring",
        ),
        pytest.param(
            '''
class Class1:
    def function_1():
        """Docstring.

        Returns:
        """
''',
            (f"4:8 {RETURNS_SECTION_IN_DOCSTR_MSG}",),
            id="method no return returns in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring.

    Returns:
    """
    return
''',
            (f"3:4 {RETURNS_SECTION_IN_DOCSTR_MSG}",),
            id="function return no value returns in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring.

    Returns:

    Returns:
    """
    return 1
''',
            (f"3:4 {MULT_RETURNS_SECTION_IN_DOCSTR_MSG % 'Returns,Returns'}",),
            id="function return multiple returns in docstring",
        ),
        pytest.param(
            '''
class Class1:
    def function_1():
        """Docstring.

        Returns:

        Returns:
        """
        return 1
''',
            (f"4:8 {MULT_RETURNS_SECTION_IN_DOCSTR_MSG % 'Returns,Returns'}",),
            id="method return multiple returns in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    return 1
''',
            (f"4:4 {RETURNS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function single return value returns not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    return 0
''',
            (f"4:4 {RETURNS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function single falsely return value returns not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    return None
''',
            (f"4:4 {RETURNS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function single None return value returns not in docstring",
        ),
        pytest.param(
            '''
async def function_1():
    """Docstring."""
    return 1
''',
            (f"4:4 {RETURNS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="async function single return value returns not in docstring",
        ),
        pytest.param(
            '''
class FooClass:
    """Docstring."""
    def function_1(self):
        """Docstring."""
        return 1
''',
            (f"6:8 {RETURNS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="method single return value returns not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    if True:
        return 1
''',
            (f"5:8 {RETURNS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function single nested return value returns not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    return 11
    return 12
''',
            (
                f"4:4 {RETURNS_SECTION_NOT_IN_DOCSTR_MSG}",
                f"5:4 {RETURNS_SECTION_NOT_IN_DOCSTR_MSG}",
            ),
            id="function multiple return value returns not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    return 11
    return
''',
            (f"4:4 {RETURNS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function multiple return first value returns not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    return
    return 12
''',
            (f"5:4 {RETURNS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function multiple return second value returns not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    yield 1
''',
            (f"4:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function single yield value yields not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    yield from tuple()
''',
            (f"4:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function single yield from value yields not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    yield 0
''',
            (f"4:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function single falsely yield value yields not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    yield None
''',
            (f"4:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function single None yield value yields not in docstring",
        ),
        pytest.param(
            '''
async def function_1():
    """Docstring."""
    yield 1
''',
            (f"4:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="async function single yield value yields not in docstring",
        ),
        pytest.param(
            '''
class FooClass:
    """Docstring."""
    def function_1(self):
        """Docstring."""
        yield 1
''',
            (f"6:8 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="method single yield value yields not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    if True:
        yield 1
''',
            (f"5:8 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function single nested yield value yields not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    yield 11
    yield 12
''',
            (
                f"4:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",
                f"5:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",
            ),
            id="function multiple yield value yields not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    yield 11
    yield
''',
            (f"4:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function multiple yield first value yields not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    yield
    yield 12
''',
            (f"5:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function multiple yield second value yields not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    yield from tuple()
    yield from list()
''',
            (
                f"4:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",
                f"5:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",
            ),
            id="function multiple yield from value yields not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    yield from tuple()
    yield
''',
            (f"4:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function multiple yield from first value yields not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring."""
    yield
    yield from list()
''',
            (f"5:4 {YIELDS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function multiple yield from second value yields not in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring.

    Yields:
    """
''',
            (f"3:4 {YIELDS_SECTION_IN_DOCSTR_MSG}",),
            id="function no yield yields in docstring",
        ),
        pytest.param(
            '''
class Class1:
    def function_1():
        """Docstring.

        Yields:
        """
''',
            (f"4:8 {YIELDS_SECTION_IN_DOCSTR_MSG}",),
            id="method no yield yields in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring.

    Yields:
    """
    yield
''',
            (f"3:4 {YIELDS_SECTION_IN_DOCSTR_MSG}",),
            id="function yield no value yields in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring.

    Yields:

    Yields:
    """
    yield 1
''',
            (f"3:4 {MULT_YIELDS_SECTION_IN_DOCSTR_MSG % 'Yields,Yields'}",),
            id="function yield multiple yields in docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring.

    Yields:

    Yields:
    """
    yield from tuple()
''',
            (f"3:4 {MULT_YIELDS_SECTION_IN_DOCSTR_MSG % 'Yields,Yields'}",),
            id="function yield from multiple yields in docstring",
        ),
        pytest.param(
            '''
class Class1:
    def function_1():
        """Docstring.

        Yields:

        Yields:
        """
        yield 1
''',
            (f"4:8 {MULT_YIELDS_SECTION_IN_DOCSTR_MSG % 'Yields,Yields'}",),
            id="method yield multiple yields in docstring",
        ),
        pytest.param(
            '''
async def function_1():
    """Docstring 1."""
''',
            (),
            id="function docstring",
        ),
        pytest.param(
            '''
async def function_1():
    """Docstring 1."""

async def function_2():
    """Docstring 2."""
''',
            (),
            id="multiple functions docstring",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
''',
            (),
            id="async function docstring",
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
def function_1(_arg_1):
    """Docstring 1."""
''',
            (),
            id="function single unused arg docstring no args",
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
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    return
''',
            (),
            id="function return no value docstring no returns section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Returns:
    """
    return 1
''',
            (),
            id="function return value docstring returns section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    def function_2():
        """Docstring 2.

        Returns:
        """
        return 1
''',
            (),
            id="function return value in nested function docstring no returns section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    async def function_2():
        """Docstring 2.

        Returns:
        """
        return 1
''',
            (),
            id="function return value in nested async function docstring no returns section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    class Class1:
        return 1
''',
            (),
            id="function return value in class docstring no returns section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Returns:
    """
    return 1
    return 2
''',
            (),
            id="function multiple return values docstring returns section",
        ),
        pytest.param(
            '''
class Class_1:
    def function_1(self):
        """Docstring 1.

        Returns:
        """
        return 1
''',
            (),
            id="method return value docstring returns section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    yield
''',
            (),
            id="function yield no value docstring no yields section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Yields:
    """
    yield 1
''',
            (),
            id="function yield value docstring yields section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Yields:
    """
    yield from tuple()
''',
            (),
            id="function yield from docstring yields section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    def function_2():
        """Docstring 2.

        Yields:
        """
        yield 1
''',
            (),
            id="function yield value in nested function docstring no yields section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    async def function_2():
        """Docstring 2.

        Yields:
        """
        yield 1
''',
            (),
            id="function yield value in nested async function docstring no yields section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    class Class1:
        yield 1
''',
            (),
            id="function yield value in class docstring no yields section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Yields:
    """
    yield 1
    yield 2
''',
            (),
            id="function multiple yield values docstring yields section",
        ),
        pytest.param(
            '''
class Class_1:
    def function_1(self):
        """Docstring 1.

        Yields:
        """
        yield 1
''',
            (),
            id="method yield value docstring yields section",
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
        pytest.param(
            """
def foo():
    pass
""",
            "conftest.py",
            (f"2:0 {DOCSTR_MISSING_FUNC_MSG}",),
            id="normal file not fixture function",
        ),
        pytest.param(
            """
@(1 + 1)
def foo():
    pass
""",
            "conftest.py",
            (f"3:0 {DOCSTR_MISSING_FUNC_MSG}",),
            id="fixture file not fixture decorator",
        ),
        pytest.param(
            """
@fixture
def foo():
    pass
""",
            "source.py",
            (f"3:0 {DOCSTR_MISSING_FUNC_MSG}",),
            id="source file fixture function",
        ),
        pytest.param(
            """
@fixture
def foo():
    pass
""",
            "conftest.py",
            (),
            id="fixture file fixture function",
        ),
        pytest.param(
            """
@fixture
def foo():
    pass
""",
            "test_.py",
            (),
            id="test file fixture function",
        ),
        pytest.param(
            """
@FIXTURE
def foo():
    pass
""",
            "conftest.py",
            (),
            id="fixture file fixture function capitalised",
        ),
        pytest.param(
            """
@fixture
@decorator
def foo():
    pass
""",
            "conftest.py",
            (),
            id="fixture file fixture function multiple decorators first",
        ),
        pytest.param(
            """
@decorator
@fixture
def foo():
    pass
""",
            "conftest.py",
            (),
            id="fixture file fixture function multiple decorators second",
        ),
        pytest.param(
            """
@pytest.fixture
def foo():
    pass
""",
            "conftest.py",
            (),
            id="fixture file fixture function prefix",
        ),
        pytest.param(
            """
@pytest.fixture(scope="module")
def foo():
    pass
""",
            "conftest.py",
            (),
            id="fixture file fixture function prefix call",
        ),
        pytest.param(
            """
@additional.pytest.fixture
def foo():
    pass
""",
            "conftest.py",
            (),
            id="fixture file fixture function nested prefix",
        ),
        pytest.param(
            """
@fixture(scope="module")
def foo():
    pass
""",
            "conftest.py",
            (),
            id="fixture file fixture function arguments",
        ),
        pytest.param(
            """
@fixture
def foo():
    pass
""",
            "tests/conftest.py",
            (),
            id="fixture file fixture function in directory",
        ),
    ],
)
def test_plugin_filename(code: str, filename: str, expected_result: tuple[str, ...]):
    """
    given: code and filename
    when: linting is run on the code
    then: the expected result is returned
    """
    assert result.get(code, filename) == expected_result
