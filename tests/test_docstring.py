"""Tests for docstring module."""

# Need access to protected functions for testing
# pylint: disable=protected-access

import pytest

from flake8_docstrings_complete import docstring

from . import factories


@pytest.mark.parametrize(
    "lines, expected_sections",
    [
        pytest.param((), (), id="empty"),
        pytest.param(("",), (), id="single not a section"),
        pytest.param(("not a section",), (), id="single not a section no colon"),
        pytest.param(("not a section:",), (), id="single not a section not after first word"),
        pytest.param(("name_1:",), (docstring._Section("name_1", ()),), id="single section"),
        pytest.param(
            (" name_1:",),
            (docstring._Section("name_1", ()),),
            id="single section leading whitespace single space",
        ),
        pytest.param(
            ("\tname_1:",),
            (docstring._Section("name_1", ()),),
            id="single section leading whitespace single tab",
        ),
        pytest.param(
            ("  name_1:",),
            (docstring._Section("name_1", ()),),
            id="single section leading whitespace multiple",
        ),
        pytest.param(
            ("name_1: ",),
            (docstring._Section("name_1", ()),),
            id="single section trailing whitespace",
        ),
        pytest.param(
            ("name_1: description",),
            (docstring._Section("name_1", ()),),
            id="single section trailing characters",
        ),
        pytest.param(
            ("name_1:", "description 1"),
            (docstring._Section("name_1", ()),),
            id="single section multiple lines",
        ),
        pytest.param(
            ("name_1:", "sub_name_1:"),
            (docstring._Section("name_1", ("sub_name_1",)),),
            id="single section single sub-section",
        ),
        pytest.param(
            ("name_1:", "sub_name_1 (text 1):"),
            (docstring._Section("name_1", ("sub_name_1",)),),
            id="single section single sub-section brackets",
        ),
        pytest.param(
            ("name_1:", " sub_name_1:"),
            (docstring._Section("name_1", ("sub_name_1",)),),
            id="single section single sub-section leading whitespace",
        ),
        pytest.param(
            ("name_1:", "sub_name_1: "),
            (docstring._Section("name_1", ("sub_name_1",)),),
            id="single section single sub-section trailing whitespace",
        ),
        pytest.param(
            ("name_1:", "sub_name_1: description 1"),
            (docstring._Section("name_1", ("sub_name_1",)),),
            id="single section single sub-section trailing characters",
        ),
        pytest.param(
            ("name_1:", "sub_name_1:", "description 1"),
            (docstring._Section("name_1", ("sub_name_1",)),),
            id="single section single sub-section other sub first",
        ),
        pytest.param(
            ("name_1:", "description 1", "sub_name_1:"),
            (docstring._Section("name_1", ("sub_name_1",)),),
            id="single section single sub-section other sub last",
        ),
        pytest.param(
            ("name_1:", "sub_name_1:", "sub_name_2:"),
            (docstring._Section("name_1", ("sub_name_1", "sub_name_2")),),
            id="single section multiple sub-sections",
        ),
        pytest.param(
            ("name_1:", "sub_name_1:", "sub_name_2:", "sub_name_3:"),
            (docstring._Section("name_1", ("sub_name_1", "sub_name_2", "sub_name_3")),),
            id="single section many sub-sections",
        ),
        pytest.param(
            ("name_1:", "description 1", "description 2"),
            (docstring._Section("name_1", ()),),
            id="single section many lines",
        ),
        pytest.param(
            ("name_1:", ""), (docstring._Section("name_1", ()),), id="single section separator"
        ),
        pytest.param(
            ("name_1:", "", "name_2:"),
            (docstring._Section("name_1", ()), docstring._Section("name_2", ())),
            id="multiple sections separator empty",
        ),
        pytest.param(
            ("name_1:", " ", "name_2:"),
            (docstring._Section("name_1", ()), docstring._Section("name_2", ())),
            id="multiple sections separator single space",
        ),
        pytest.param(
            ("name_1:", "\t", "name_2:"),
            (docstring._Section("name_1", ()), docstring._Section("name_2", ())),
            id="multiple sections separator single tab",
        ),
        pytest.param(
            ("name_1:", "  ", "name_2:"),
            (docstring._Section("name_1", ()), docstring._Section("name_2", ())),
            id="multiple sections separator multiple whitespace",
        ),
        pytest.param(
            ("name_1:", "sub_name_1:", "", "name_2:"),
            (docstring._Section("name_1", ("sub_name_1",)), docstring._Section("name_2", ())),
            id="multiple sections first has sub-section",
        ),
        pytest.param(
            ("name_1:", "", "name_2:", "sub_name_1:"),
            (docstring._Section("name_1", ()), docstring._Section("name_2", ("sub_name_1",))),
            id="multiple sections last has sub-section",
        ),
        pytest.param(
            ("name_1:", "", "name_2:", "", "name_3:"),
            (
                docstring._Section("name_1", ()),
                docstring._Section("name_2", ()),
                docstring._Section("name_3", ()),
            ),
            id="many sections",
        ),
    ],
)
def test__get_sections(
    lines: tuple[()] | tuple[str, ...],
    expected_sections: tuple[()] | tuple[docstring._Section, ...],
):
    """
    arrange: given lines of a docstring
    act: when _get_sections is called with the lines
    assert: then the expected sections are returned.
    """
    assert isinstance(lines, tuple)
    assert isinstance(expected_sections, tuple)

    returned_sections = tuple(docstring._get_sections(lines=lines))

    assert returned_sections == expected_sections


@pytest.mark.parametrize(
    "value, expected_docstring",
    [
        pytest.param("", docstring.Docstring(), id="empty"),
        pytest.param("short description", docstring.Docstring(), id="short description"),
        pytest.param(
            """short description

long description""",
            docstring.Docstring(),
            id="short and long description",
        ),
        pytest.param(
            """short description
Args:
    """,
            docstring.Docstring(args=()),
            id="args empty",
        ),
        pytest.param(
            """short description
Args:
    arg_1:
    """,
            docstring.Docstring(args=("arg_1",)),
            id="args single",
        ),
        pytest.param(
            """short description
Args:
    arg_1:
    arg_2:
    """,
            docstring.Docstring(args=("arg_1", "arg_2")),
            id="args multiple",
        ),
        pytest.param(
            """short description
args:
    arg_1:
    """,
            docstring.Docstring(args=("arg_1",)),
            id="args lower case",
        ),
        pytest.param(
            """short description
Arguments:
    arg_1:
    """,
            docstring.Docstring(args=("arg_1",)),
            id="args alternate Arguments",
        ),
        pytest.param(
            """short description
Parameters:
    arg_1:
    """,
            docstring.Docstring(args=("arg_1",)),
            id="args alternate Parameters",
        ),
        pytest.param(
            """short description
Attrs:
    """,
            docstring.Docstring(attrs=()),
            id="attrs empty",
        ),
        pytest.param(
            """short description
Attrs:
    attr_1:
    """,
            docstring.Docstring(args=("attr_1",)),
            id="attrs single",
        ),
        pytest.param(
            """short description
Attrs:
    attr_1:
    attr_2:
    """,
            docstring.Docstring(args=("attr_1", "attr_2")),
            id="attrs multiple",
        ),
        pytest.param(
            """short description
attrs:
    attr_1:
    """,
            docstring.Docstring(args=("attr_1",)),
            id="attrs lower case",
        ),
        pytest.param(
            """short description
Attributes:
    attr_1:
    """,
            docstring.Docstring(args=("attr_1",)),
            id="attrs alternate Attributes",
        ),
    ],
)
def test_parse(value: str, expected_docstring: docstring.Docstring):
    """
    arrange: given docstring value
    act: when parse is called with the docstring
    assert: then the expected docstring information is returned.
    """
    returned_docstring = docstring.parse(value=value)

    assert returned_docstring == expected_docstring
