"""Unit tests for plugin except for args rules."""

# The lines represent the number of test cases
# pylint: disable=too-many-lines

from __future__ import annotations

import pytest

from flake8_docstrings_complete import (
    DOCSTR_MISSING_MSG,
    MULT_RETURNS_SECTIONS_IN_DOCSTR_MSG,
    MULT_YIELDS_SECTIONS_IN_DOCSTR_MSG,
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
            (f"2:0 {DOCSTR_MISSING_MSG}",),
            id="function docstring missing return",
        ),
        pytest.param(
            """
def _function_1():
    return
""",
            (f"2:0 {DOCSTR_MISSING_MSG}",),
            id="private function docstring missing return",
        ),
        pytest.param(
            """
@overload
def function_1():
    ...
""",
            (),
            id="function docstring missing overload",
        ),
        pytest.param(
            """
@overload()
def function_1():
    ...
""",
            (),
            id="function docstring missing overload call",
        ),
        pytest.param(
            """
@typing.overload
def function_1():
    ...
""",
            (),
            id="function docstring missing overload attr",
        ),
        pytest.param(
            """
def function_1():
    return

def function_2():
    return
""",
            (f"2:0 {DOCSTR_MISSING_MSG}", f"5:0 {DOCSTR_MISSING_MSG}"),
            id="multiple functions docstring missing return",
        ),
        pytest.param(
            """
def function_1():
    pass
""",
            (f"2:0 {DOCSTR_MISSING_MSG}",),
            id="function docstring missing expression not constant",
        ),
        pytest.param(
            """
def function_1():
    1
""",
            (f"2:0 {DOCSTR_MISSING_MSG}",),
            id="function docstring missing expression constnant not string",
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
def _function_1():
    """Docstring.

    Returns:
    """
''',
            (f"3:4 {RETURNS_SECTION_IN_DOCSTR_MSG}",),
            id="private function no return returns in docstring",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1():
        """Docstring.

        Returns:
        """
''',
            (f"5:8 {RETURNS_SECTION_IN_DOCSTR_MSG}",),
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
            (f"3:4 {MULT_RETURNS_SECTIONS_IN_DOCSTR_MSG % 'Returns,Returns'}",),
            id="function return multiple returns in docstring",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1():
        """Docstring.

        Returns:

        Returns:
        """
        return 1
''',
            (f"5:8 {MULT_RETURNS_SECTIONS_IN_DOCSTR_MSG % 'Returns,Returns'}",),
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
def _function_1():
    """Docstring."""
    yield 1
''',
            (),
            id="private function single yield value yields not in docstring",
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
def _function_1():
    """Docstring.

    Yields:
    """
''',
            (f"3:4 {YIELDS_SECTION_IN_DOCSTR_MSG}",),
            id="private function no yield yields in docstring",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1():
        """Docstring.

        Yields:
        """
''',
            (f"5:8 {YIELDS_SECTION_IN_DOCSTR_MSG}",),
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
            (f"3:4 {MULT_YIELDS_SECTIONS_IN_DOCSTR_MSG % 'Yields,Yields'}",),
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
            (f"3:4 {MULT_YIELDS_SECTIONS_IN_DOCSTR_MSG % 'Yields,Yields'}",),
            id="function yield from multiple yields in docstring",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1():
        """Docstring.

        Yields:

        Yields:
        """
        yield 1
''',
            (f"5:8 {MULT_YIELDS_SECTIONS_IN_DOCSTR_MSG % 'Yields,Yields'}",),
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
class Class1:
    """Docstring."""
    def function_1(self):
        return
''',
            (f"4:4 {DOCSTR_MISSING_MSG}",),
            id="method docstring missing return",
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
def _function_1():
    """Docstring 1.

    Returns:
    """
    return 1
''',
            (),
            id="private function return value docstring returns section",
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
        """Docstring."""
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
class Class1:
    """Docstring."""
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
class Class1:
    """Docstring.

    Attrs:
        function_1:
    """
    @property
    def function_1(self):
        """Docstring 1."""
        return 1
''',
            (),
            id="property return value docstring no returns section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring.

    Attrs:
        function_1:
    """
    @cached_property
    def function_1(self):
        """Docstring 1."""
        return 1
''',
            (),
            id="cached_property return value docstring no returns section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring.

    Attrs:
        function_1:
    """
    @functools.cached_property
    def function_1(self):
        """Docstring 1."""
        return 1
''',
            (),
            id="functools.cached_property return value docstring no returns section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring.

    Attrs:
        function_1:
    """
    @property
    async def function_1(self):
        """Docstring 1."""
        return 1
''',
            (),
            id="async property return value docstring no returns section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring.

    Attrs:
        function_1:
    """
    @property()
    def function_1(self):
        """Docstring 1."""
        return 1
''',
            (),
            id="property call return value docstring no returns section",
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
def _function_1():
    """Docstring 1.

    Yields:
    """
    yield 1
''',
            (),
            id="private function yield value docstring yields section",
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
        """Docstring."""
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
class Class1:
    """Docstring."""
    def function_1(self):
        """Docstring 1.

        Yields:
        """
        yield 1
''',
            (),
            id="method yield value docstring yields section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring.

    Attrs:
        function_1:
    """
    @property
    def function_1(self):
        """Docstring 1."""
        yield 1
''',
            (),
            id="property yield value docstring no yields section",
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
            (f"2:0 {DOCSTR_MISSING_MSG}",),
            id="not test file",
        ),
        pytest.param(
            """
def foo():
    pass
""",
            "test_.py",
            (f"2:0 {DOCSTR_MISSING_MSG}",),
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
            (f"2:0 {DOCSTR_MISSING_MSG}",),
            id="normal file not fixture function",
        ),
        pytest.param(
            """
@fixture
def foo():
    pass
""",
            "source.py",
            (f"3:0 {DOCSTR_MISSING_MSG}",),
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
