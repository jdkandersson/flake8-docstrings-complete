"""Tests for docstring module."""

# Need access to protected functions for testing
# pylint: disable=protected-access

import pytest

from flake8_docstrings_complete import docstring


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
    given: lines of a docstring
    when: _get_sections is called with the lines
    then: the expected sections are returned.
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
            docstring.Docstring(args=(), args_sections=("Args",)),
            id="args empty",
        ),
        pytest.param(
            """short description

Args:
    arg_1:
    """,
            docstring.Docstring(args=("arg_1",), args_sections=("Args",)),
            id="args single",
        ),
        pytest.param(
            """short description

Args:
    arg_1:
    arg_2:
    """,
            docstring.Docstring(args=("arg_1", "arg_2"), args_sections=("Args",)),
            id="args multiple",
        ),
        pytest.param(
            """short description

args:
    arg_1:
    """,
            docstring.Docstring(args=("arg_1",), args_sections=("args",)),
            id="args lower case",
        ),
        pytest.param(
            """short description

Arguments:
    arg_1:
    """,
            docstring.Docstring(args=("arg_1",), args_sections=("Arguments",)),
            id="args alternate Arguments",
        ),
        pytest.param(
            """short description

Parameters:
    arg_1:
    """,
            docstring.Docstring(args=("arg_1",), args_sections=("Parameters",)),
            id="args alternate Parameters",
        ),
        pytest.param(
            """short description

Args:
    arg_1:

Parameters:
    arg_2:
    """,
            docstring.Docstring(args=("arg_1",), args_sections=("Args", "Parameters")),
            id="args multiple sections",
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
            docstring.Docstring(attrs=("attr_1",)),
            id="attrs single",
        ),
        pytest.param(
            """short description

Attrs:
    attr_1:
    attr_2:
    """,
            docstring.Docstring(attrs=("attr_1", "attr_2")),
            id="attrs multiple",
        ),
        pytest.param(
            """short description

attrs:
    attr_1:
    """,
            docstring.Docstring(attrs=("attr_1",)),
            id="attrs lower case",
        ),
        pytest.param(
            """short description

Attributes:
    attr_1:
    """,
            docstring.Docstring(attrs=("attr_1",)),
            id="attrs alternate Attributes",
        ),
        pytest.param(
            """short description

Returns:
    """,
            docstring.Docstring(returns=True, returns_sections=("Returns",)),
            id="returns empty",
        ),
        pytest.param(
            """short description

Returns:
    The return value.
    """,
            docstring.Docstring(returns=True, returns_sections=("Returns",)),
            id="returns single line",
        ),
        pytest.param(
            """short description

Return:
    """,
            docstring.Docstring(returns=True, returns_sections=("Return",)),
            id="returns alternate",
        ),
        pytest.param(
            """short description

Returns:

Returns:
    """,
            docstring.Docstring(returns=True, returns_sections=("Returns", "Returns")),
            id="mutiple returns",
        ),
        pytest.param(
            """short description

Returns:

Return:
    """,
            docstring.Docstring(returns=True, returns_sections=("Returns", "Return")),
            id="mutiple returns alternate",
        ),
        pytest.param(
            """short description

Yields:
    """,
            docstring.Docstring(yields=True, yields_sections=("Yields",)),
            id="yields empty",
        ),
        pytest.param(
            """short description

Yields:
    The return value.
    """,
            docstring.Docstring(yields=True, yields_sections=("Yields",)),
            id="yields single line",
        ),
        pytest.param(
            """short description

Yield:
    """,
            docstring.Docstring(yields=True, yields_sections=("Yield",)),
            id="yields alternate",
        ),
        pytest.param(
            """short description

Yields:

Yields:
    """,
            docstring.Docstring(yields=True, yields_sections=("Yields", "Yields")),
            id="mutiple yields",
        ),
        pytest.param(
            """short description

Yields:

Yield:
    """,
            docstring.Docstring(yields=True, yields_sections=("Yields", "Yield")),
            id="mutiple yields alternate",
        ),
        pytest.param(
            """short description

Raises:
    """,
            docstring.Docstring(raises=()),
            id="raises empty",
        ),
        pytest.param(
            """short description

Raises:
    exc_1:
    """,
            docstring.Docstring(raises=("exc_1",)),
            id="raises single",
        ),
        pytest.param(
            """short description

Raises:
    exc_1:
    exc_2:
    """,
            docstring.Docstring(raises=("exc_1", "exc_2")),
            id="raises multiple",
        ),
        pytest.param(
            """short description

raises:
    exc_1:
    """,
            docstring.Docstring(raises=("exc_1",)),
            id="raises lower case",
        ),
        pytest.param(
            """short description

Attrs:
    attr_1:

Args:
    arg_1:

Returns:
    The return value.

Yields:
    The yield value.

Raises:
    exc_1:
    """,
            docstring.Docstring(
                args=("arg_1",),
                args_sections=("Args",),
                attrs=("attr_1",),
                returns=True,
                returns_sections=("Returns",),
                yields=True,
                yields_sections=("Yields",),
                raises=("exc_1",),
            ),
            id="all defined",
        ),
    ],
)
def test_parse(value: str, expected_docstring: docstring.Docstring):
    """
    given: docstring value
    when: parse is called with the docstring
    then: the expected docstring information is returned.
    """
    returned_docstring = docstring.parse(value=value)

    assert returned_docstring == expected_docstring
