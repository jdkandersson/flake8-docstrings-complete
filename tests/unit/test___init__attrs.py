"""Unit tests for attrs checks in the plugin."""

from __future__ import annotations

import pytest

from flake8_docstrings_complete import (
    ATTR_IN_DOCSTR_MSG,
    ATTR_NOT_IN_DOCSTR_MSG,
    ATTRS_SECTION_IN_DOCSTR_MSG,
    ATTRS_SECTION_NOT_IN_DOCSTR_MSG,
    MULT_ATTRS_SECTIONS_IN_DOCSTR_MSG,
)

from . import result


@pytest.mark.parametrize(
    "code, expected_result",
    [
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    attr_1 = "value 1"
''',
            (f"3:4 {ATTRS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="class has single class attr docstring no attrs section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    def __init__(self):
        """Docstring 2."""
        self.attr_1 = "value 1"
''',
            (f"3:4 {ATTRS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="class has single __init__ attr docstring no attrs section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    def method_1(self):
        """Docstring 2."""
        self.attr_1 = "value 1"
''',
            (f"3:4 {ATTRS_SECTION_NOT_IN_DOCSTR_MSG}",),
            id="class has single method attr docstring no attrs section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_1:
    """
''',
            (f"3:4 {ATTRS_SECTION_IN_DOCSTR_MSG}",),
            id="class has no attrs docstring attrs section",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_1:

    Attrs:
        attr_1:
    """
    attr_1 = "value 1"
''',
            (f"3:4 {MULT_ATTRS_SECTIONS_IN_DOCSTR_MSG % 'Attrs,Attrs'}",),
            id="class has single attrs docstring multiple attrs sections same name",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_1:

    Attributes:
        attr_1:
    """
    attr_1 = "value 1"
''',
            (f"3:4 {MULT_ATTRS_SECTIONS_IN_DOCSTR_MSG % 'Attrs,Attributes'}",),
            id="class has single attrs docstring multiple attrs sections alternate name",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
    """
    attr_1 = "value 1"
''',
            (f"7:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",),
            id="class has single attr docstring no attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
    """
    _attr_1 = "value 1"
''',
            (f"3:4 {ATTRS_SECTION_IN_DOCSTR_MSG}",),
            id="class has single unused attr docstring attrs",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
    """
    def __init__(self):
        """Docstring 2."

    attr_1 = "value 1"
''',
            (f"10:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",),
            id="class has single attr after init docstring no attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
    """
    def __init__(self):
        """Docstring 2."
        attr_1 = "value 1"
''',
            (f"9:8 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",),
            id="class has single attr in init docstring no attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
    """
    def method_1(self):
        """Docstring 2."
        self.attr_1 = "value 1"
''',
            (f"9:8 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",),
            id="class has single attr in method docstring no attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
    """
    async def method_1(self):
        """Docstring 2."
        self.attr_1 = "value 1"
''',
            (f"9:8 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",),
            id="class has single attr in async method docstring no attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
    """
    @classmethod
    def method_1(cls):
        """Docstring 2."
        cls.attr_1 = "value 1"
''',
            (f"9:8 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",),
            id="class has single attr in classmethod method docstring no attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
    """
    attr_1 = "value 1"
    attr_2 = "value 2"
        ''',
            (
                f"7:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",
                f"8:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_2'}",
            ),
            id="class multiple attrs docstring no attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
    """
    _attr_1 = "value 1"
    attr_2 = "value 2"
        ''',
            (f"8:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_2'}",),
            id="class multiple attrs first private docstring no attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
    """
    attr_1 = "value 1"
    _attr_2 = "value 2"
        ''',
            (f"7:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",),
            id="class multiple attrs second private docstring no attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_1:
    """
    attr_1 = "value 1"
    attr_2 = "value 2"
''',
            (f"9:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_2'}",),
            id="class multiple attrs docstring single attr first",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_2:
    """
    attr_1 = "value 1"
    attr_2 = "value 2"
''',
            (f"8:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",),
            id="class multiple attrs docstring single attr second",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_2:
    """
    attr_1 = "value 1"
''',
            (
                f"8:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",
                f"3:4 {ATTR_IN_DOCSTR_MSG % 'attr_2'}",
            ),
            id="class has single attr docstring attr different",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_2:
        attr_3:
    """
    attr_1 = "value 1"
        ''',
            (
                f"9:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",
                f"3:4 {ATTR_IN_DOCSTR_MSG % 'attr_2'}",
                f"3:4 {ATTR_IN_DOCSTR_MSG % 'attr_3'}",
            ),
            id="class single attr docstring multiple attrs different",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_3:
        attr_4:
    """
    attr_1 = "value 1"
    attr_2 = "value 2"
        ''',
            (
                f"9:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}",
                f"10:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_2'}",
                f"3:4 {ATTR_IN_DOCSTR_MSG % 'attr_3'}",
                f"3:4 {ATTR_IN_DOCSTR_MSG % 'attr_4'}",
            ),
            id="class multiple attr docstring multiple attrs different",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_2:
        attr_3:
    """
    attr_1 = "value 1"
    attr_2 = "value 2"
        ''',
            (f"9:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_1'}", f"3:4 {ATTR_IN_DOCSTR_MSG % 'attr_3'}"),
            id="class multiple attr docstring multiple attrs first different",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_1:
        attr_3:
    """
    attr_1 = "value 1"
    attr_2 = "value 2"
        ''',
            (f"10:4 {ATTR_NOT_IN_DOCSTR_MSG % 'attr_2'}", f"3:4 {ATTR_IN_DOCSTR_MSG % 'attr_3'}"),
            id="class multiple attr docstring multiple attrs second different",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_1:
    """
    attr_1 = "value 1"
''',
            (),
            id="class single attr docstring single attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_1:
    """
    def __init__(self):
        """Docstring 2."""
        self.attr_1 = "value 1"
''',
            (),
            id="class single attr init docstring single attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_1:
    """
    def method_1(self):
        """Docstring 2."""
        self.attr_1 = "value 1"
''',
            (),
            id="class single attr method docstring single attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_1:
    """
    @classmethod
    def method_1(cls):
        """Docstring 2."""
        cls.attr_1 = "value 1"
''',
            (),
            id="class single attr classmethod docstring single attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        _attr_1:
    """
    _attr_1 = "value 1"
''',
            (),
            id="class single private attr docstring single attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    _attr_1 = "value 1"
    """
''',
            (),
            id="class single private attr docstring single attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    def __init__(self):
        """Docstring 2."""
        var_1 = "value 1"
    """
''',
            (),
            id="class single var init docstring single attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    def method_1(self):
        """Docstring 2."""
        var_1 = "value 1"
    """
''',
            (),
            id="class single var method docstring single attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    @classmethod
    def method_1(cls):
        """Docstring 2."""
        var_1 = "value 1"
    """
''',
            (),
            id="class single var classmethod docstring single attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_1:
        attr_2:
    """
    attr_1 = "value 1"
    attr_2 = "value 2"
''',
            (),
            id="class multiple attr docstring multiple attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_2:
    """
    _attr_1 = "value 1"
    attr_2 = "value 2"
''',
            (),
            id="class multiple attr first private docstring single attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1.

    Attrs:
        attr_1:
    """
    attr_1 = "value 1"
    _attr_2 = "value 2"
''',
            (),
            id="class multiple attr second private docstring single attr",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    class Class2:
        """Docstring 2.

        Attrs:
            attr_1:
        """
        attr_1 = "value 1"
''',
            (),
            id="nested class single attr docstring no attrs",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    def method_1(self):
        """Docstring 2."""
        lambda self: self.attr_1 = "value 1"
''',
            (),
            id="class single attr method lambda docstring no attrs",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    def method_1(self):
        """Docstring 2."""
        def nested_funciont_1(self):
            """Docstring 3."""
            self.attr_1 = "value 1"
''',
            (),
            id="class single attr method nested method docstring no attrs",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    def method_1(self):
        """Docstring 2."""
        async def nested_funciont_1(self):
            """Docstring 3."""
            self.attr_1 = "value 1"
''',
            (),
            id="class single attr method nested async method docstring no attrs",
        ),
        pytest.param(
            '''
class Class1:
    """Docstring 1."""
    def method_1(self):
        """Docstring 2."""
        def nested_funciont_1(cls):
            """Docstring 3."""
            cls.attr_1 = "value 1"
''',
            (),
            id="class single attr method nested classmethod docstring no attrs",
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
