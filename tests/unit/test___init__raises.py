"""Unit tests for raises checks in the plugin."""

from __future__ import annotations

import pytest

from flake8_docstrings_complete.raises import (
    DUPLICATE_EXC_MSG,
    EXC_IN_DOCSTR_MSG,
    EXC_NOT_IN_DOCSTR_MSG,
    MULT_RAISES_SECTIONS_IN_DOCSTR_MSG,
    RAISES_SECTION_IN_DOCSTR_MSG,
    RAISES_SECTION_NOT_IN_DOCSTR_MSG,
    RE_RAISE_NO_EXC_IN_DOCSTR_MSG,
)

from . import result


@pytest.mark.parametrize(
    "code, expected_result",
    [
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    raise Exc1
''',
            (f"3:4 {RAISES_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="function raises single exc docstring no raises section",
        ),
        pytest.param(
            '''
def _function_1():
    """Docstring 1."""
    raise Exc1
''',
            (),
            id="private function raises single exc docstring no raises section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    raise Exc1

def function_2():
    """Docstring 2."""
    raise Exc2
''',
            (
                f"3:4 {RAISES_SECTION_NOT_IN_DOCSTR_MSG}",
                f"7:4 {RAISES_SECTION_NOT_IN_DOCSTR_MSG}",
            ),
            id="multiple function raises single exc docstring no raises section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
    """
''',
            (f"3:4 {RAISES_SECTION_IN_DOCSTR_MSG}",),
            id="function raises no exc docstring raises section",
        ),
        pytest.param(
            '''
def _function_1():
    """Docstring 1.

    Raises:
    """
''',
            (f"3:4 {RAISES_SECTION_IN_DOCSTR_MSG}",),
            id="private function raises no exc docstring raises section",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:

    Raises:
        Exc1:
    """
    raise Exc1
''',
            (f"3:4 {MULT_RAISES_SECTIONS_IN_DOCSTR_MSG % 'Raises,Raises'}",),
            id="function raises single excs docstring multiple raises sections same name",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:

    Raise:
        Exc1:
    """
    raise Exc1
''',
            (f"3:4 {MULT_RAISES_SECTIONS_IN_DOCSTR_MSG % 'Raises,Raise'}",),
            id="function raises single excs docstring multiple raises sections different name",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
    """
    raise Exc1
''',
            (f"7:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",),
            id="function raises single exc docstring no exc",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
    """
    raise Exc1
    raise
''',
            (f"7:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",),
            id="function raises single exc and single no exc docstring no exc",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
    """
    raise Exc1()
''',
            (f"7:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",),
            id="function raises single exc call docstring no exc",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
    """
    raise module.Exc1
''',
            (f"7:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",),
            id="function raises single nested exc docstring no exc",
        ),
        pytest.param(
            '''
async def function_1():
    """Docstring 1.

    Raises:
    """
    raise Exc1
''',
            (f"7:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",),
            id="async function raises single exc docstring no exc",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
    """
    raise Exc1
    raise Exc2
        ''',
            (f"7:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}", f"8:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc2'}"),
            id="function multiple excs docstring no exc",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
    """
    def function_2():
        """Docstring 2.

        Raises:
            Exc1:
        """
        raise Exc1
    raise Exc2
        ''',
            (f"14:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc2'}",),
            id="function multiple excs first nested function",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
    """
    async def function_2():
        """Docstring 2.

        Raises:
            Exc1:
        """
        raise Exc1
    raise Exc2
        ''',
            (f"14:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc2'}",),
            id="function multiple excs first nested async function",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
    """
    class Class1:
        """Docstring 2."""
        raise Exc1
    raise Exc2
        ''',
            (f"10:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc2'}",),
            id="function multiple excs first nested class",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
    """
    raise Exc1
    def function_2():
        """Docstring 2.

        Raises:
            Exc2:
        """
        raise Exc2
        ''',
            (f"7:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",),
            id="function multiple excs second nested function",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
    """
    raise Exc1
    raise Exc2
''',
            (f"9:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc2'}",),
            id="function multiple excs docstring single exc first",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc2:
    """
    raise Exc1
    raise Exc2
''',
            (f"8:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",),
            id="function multiple excs docstring single exc second",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc2:
    """
    raise Exc1
''',
            (
                f"8:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",
                f"3:4 {EXC_IN_DOCSTR_MSG % 'Exc2'}",
            ),
            id="function raises single exc docstring exc different",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc2:
        Exc3:
    """
    raise Exc1
        ''',
            (
                f"9:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",
                f"3:4 {EXC_IN_DOCSTR_MSG % 'Exc2'}",
                f"3:4 {EXC_IN_DOCSTR_MSG % 'Exc3'}",
            ),
            id="function single exc docstring multiple exc different",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc3:
        Exc4:
    """
    raise Exc1
    raise Exc2
        ''',
            (
                f"9:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",
                f"10:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc2'}",
                f"3:4 {EXC_IN_DOCSTR_MSG % 'Exc3'}",
                f"3:4 {EXC_IN_DOCSTR_MSG % 'Exc4'}",
            ),
            id="function multiple exc docstring multiple exc different",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc3:
        Exc2:
    """
    raise Exc1
    raise Exc2
        ''',
            (f"9:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}", f"3:4 {EXC_IN_DOCSTR_MSG % 'Exc3'}"),
            id="function multiple exc docstring multiple exc first different",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
        Exc3:
    """
    raise Exc1
    raise Exc2
        ''',
            (f"10:10 {EXC_NOT_IN_DOCSTR_MSG % 'Exc2'}", f"3:4 {EXC_IN_DOCSTR_MSG % 'Exc3'}"),
            id="function multiple exc docstring multiple exc last different",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    raise
''',
            (
                f"3:4 {RAISES_SECTION_NOT_IN_DOCSTR_MSG}",
                f"3:4 {RE_RAISE_NO_EXC_IN_DOCSTR_MSG}",
            ),
            id="function single raise no exc docstring no raises exc",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1(self):
        """Docstring 1."""
        raise
''',
            (
                f"5:8 {RAISES_SECTION_NOT_IN_DOCSTR_MSG}",
                f"5:8 {RE_RAISE_NO_EXC_IN_DOCSTR_MSG}",
            ),
            id="method raise no exc docstring no raises",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
    """
    raise
''',
            (f"3:4 {RE_RAISE_NO_EXC_IN_DOCSTR_MSG}",),
            id="function raise no exc docstring raises empty",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
        Exc1:
    """
    raise Exc1
''',
            (f"3:4 {DUPLICATE_EXC_MSG}" % "Exc1",),
            id="function single raise docstring raises duplicate",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
        Exc1:
        Exc1:
    """
    raise Exc1
''',
            (f"3:4 {DUPLICATE_EXC_MSG}" % "Exc1",),
            id="function single raise docstring raises duplicate many",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
        Exc1:
        Exc2:
    """
    raise Exc1
    raise Exc2
''',
            (f"3:4 {DUPLICATE_EXC_MSG}" % "Exc1",),
            id="function multiple raise docstring raises duplicate first",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
        Exc2:
        Exc2:
    """
    raise Exc1
    raise Exc2
''',
            (f"3:4 {DUPLICATE_EXC_MSG}" % "Exc2",),
            id="function multiple raise docstring raises duplicate second",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
        Exc1:
        Exc2:
        Exc2:
    """
    raise Exc1
    raise Exc2
''',
            (
                f"3:4 {DUPLICATE_EXC_MSG}" % "Exc1",
                f"3:4 {DUPLICATE_EXC_MSG}" % "Exc2",
            ),
            id="function multiple raise docstring raises duplicate all",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
      Exc1:
    """
    raise
''',
            (),
            id="function single raise no exc docstring raises exc",
        ),
        pytest.param(
            '''
def _function_1():
    """Docstring 1.

    Raises:
      Exc1:
    """
    raise
''',
            (),
            id="private function single raise no exc docstring raises exc",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
    """
    raise Exc1
''',
            (),
            id="function single raise exc docstring raises",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    def function_2():
        """Docstring 2.

        Raises:
            Exc1:
        """
        raise Exc1
''',
            (),
            id="function single nested function exc docstring no raises",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    async def function_2():
        """Docstring 2.

        Raises:
            Exc1:
        """
        raise Exc1
''',
            (),
            id="function single nested async function exc docstring no raises",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1."""
    class Class1:
        """Docstring 2."""
        raise Exc1
''',
            (),
            id="function single nested class exc docstring no raises",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
    """
    raise Exc1()
''',
            (),
            id="function single exc call docstring single exc",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
    """
    raise (lambda: True)()
''',
            (),
            id="function single exc lambda docstring single exc",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
    """
    raise module.Exc1
''',
            (),
            id="function single exc attribute docstring single exc",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
    """
    raise module.Exc1()
''',
            (),
            id="function single exc attribute call docstring single exc",
        ),
        pytest.param(
            '''
def function_1():
    """Docstring 1.

    Raises:
        Exc1:
        Exc2:
    """
    raise Exc1
    raise Exc2
''',
            (),
            id="function multiple exc docstring multiple exc",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1(self):
        """Docstring 1."""
        raise Exc1
''',
            (f"5:8 {RAISES_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="method raises single exc docstring no raises section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1(self):
        """Docstring 1.

        Raises:
        """
''',
            (f"5:8 {RAISES_SECTION_IN_DOCSTR_MSG}",),
            id="method raises no exc docstring raises section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1(self):
        """Docstring 1.

        Raises:
        """
        raise Exc1
''',
            (f"9:14 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",),
            id="method raises single exc docstring no exc",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    @staticmethod
    def function_1():
        """Docstring 1.

        Raises:
        """
        raise Exc1
''',
            (f"10:14 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",),
            id="method raises single exc docstring no exc staticmethod",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    @classmethod
    def function_1(cls):
        """Docstring 1.

        Raises:
        """
        raise Exc1
''',
            (f"10:14 {EXC_NOT_IN_DOCSTR_MSG % 'Exc1'}",),
            id="method raises single exc docstring no exc classmethod",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    def function_1(self):
        """Docstring 1.

        Raises:
            Exc1:
        """
        raise Exc1
''',
            (),
            id="method single exc docstring single exc",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    @staticmethod
    def function_1():
        """Docstring 1.

        Raises:
            Exc1:
        """
        raise Exc1
''',
            (),
            id="method single exc docstring single exc staticmethod",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring."""
    @classmethod
    def function_1(cls):
        """Docstring 1.

        Raises:
            Exc1:
        """
        raise Exc1
''',
            (),
            id="method single exc docstring single exc classmethod",
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
