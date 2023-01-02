"""The raises section checks."""

from __future__ import annotations

import ast
from typing import Iterable, Iterator

from . import docstring, types_
from .constants import ERROR_CODE_PREFIX, MORE_INFO_BASE

RAISES_SECTION_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}050"
RAISES_SECTION_NOT_IN_DOCSTR_MSG = (
    f"{RAISES_SECTION_NOT_IN_DOCSTR_CODE} a function/ method that raises an exception should have "
    "the raises section in the docstring"
    f"{MORE_INFO_BASE}{RAISES_SECTION_NOT_IN_DOCSTR_CODE.lower()}"
)
RAISES_SECTION_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}051"
RAISES_SECTION_IN_DOCSTR_MSG = (
    f"{RAISES_SECTION_IN_DOCSTR_CODE} a function/ method that does not raise an exception should "
    "not have the raises section in the docstring"
    f"{MORE_INFO_BASE}{RAISES_SECTION_IN_DOCSTR_CODE.lower()}"
)
MULT_RAISES_SECTIONS_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}052"
MULT_RAISES_SECTIONS_IN_DOCSTR_MSG = (
    f"{MULT_RAISES_SECTIONS_IN_DOCSTR_CODE} a docstring should only contain a single raises "
    "section, found %s"
    f"{MORE_INFO_BASE}{MULT_RAISES_SECTIONS_IN_DOCSTR_CODE.lower()}"
)
EXC_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}053"
EXC_NOT_IN_DOCSTR_MSG = (
    f'{EXC_NOT_IN_DOCSTR_CODE} "%s" exception should be described in the docstring{MORE_INFO_BASE}'
    f"{EXC_NOT_IN_DOCSTR_CODE.lower()}"
)
EXC_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}054"
EXC_IN_DOCSTR_MSG = (
    f'{EXC_IN_DOCSTR_CODE} "%s" exception should not be described in the docstring{MORE_INFO_BASE}'
    f"{EXC_IN_DOCSTR_CODE.lower()}"
)
RE_RAISE_NO_EXC_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}055"
RE_RAISE_NO_EXC_IN_DOCSTR_MSG = (
    f"{RE_RAISE_NO_EXC_IN_DOCSTR_CODE} a function/ method that re-raises exceptions should "
    "describe at least one exception in the raises section of the docstring"
    f"{MORE_INFO_BASE}{RE_RAISE_NO_EXC_IN_DOCSTR_CODE.lower()}"
)


def _get_exc_node(node: ast.Raise) -> types_.Node | None:
    """Get the exception value from raise.

    Args:
        node: The raise node.

    Returns:
        The exception node.
    """
    if isinstance(node.exc, ast.Name):
        return types_.Node(
            name=node.exc.id, lineno=node.exc.lineno, col_offset=node.exc.col_offset
        )
    if isinstance(node.exc, ast.Attribute):
        return types_.Node(
            name=node.exc.attr, lineno=node.exc.lineno, col_offset=node.exc.col_offset
        )
    if isinstance(node.exc, ast.Call):
        if isinstance(node.exc.func, ast.Name):
            return types_.Node(
                name=node.exc.func.id,
                lineno=node.exc.func.lineno,
                col_offset=node.exc.func.col_offset,
            )
        if isinstance(node.exc.func, ast.Attribute):
            return types_.Node(
                name=node.exc.func.attr,
                lineno=node.exc.func.lineno,
                col_offset=node.exc.func.col_offset,
            )

    return None


def check(
    docstr_info: docstring.Docstring, docstr_node: ast.Constant, raise_nodes: Iterable[ast.Raise]
) -> Iterator[types_.Problem]:
    """Check that all raised exceptions arguments are described in the docstring.

    Check the function/ method has at most one raises section.
    Check that all raised exceptions of the function/ method are documented.
    Check that a function/ method that doesn't raise exceptions does not have a raises section.

    Args:
        docstr_info: Information about the docstring.
        docstr_node: The docstring node.
        raise_nodes: The raise nodes.

    Yields:
        All the problems with exceptions.
    """
    all_excs = list(_get_exc_node(node) for node in raise_nodes)
    has_raise_no_value = any(exc is None for exc in all_excs)
    all_raise_no_value = all(exc is None for exc in all_excs)

    # Check that raises section is in docstring if function/ method raises exceptions
    if all_excs and docstr_info.raises is None:
        yield types_.Problem(
            docstr_node.lineno, docstr_node.col_offset, RAISES_SECTION_NOT_IN_DOCSTR_MSG
        )
    # Check that raises section is not in docstring if function/ method raises no exceptions
    if not all_excs and docstr_info.raises is not None:
        yield types_.Problem(
            docstr_node.lineno, docstr_node.col_offset, RAISES_SECTION_IN_DOCSTR_MSG
        )
    # Check for empty raises section
    if (all_excs and all_raise_no_value) and (
        docstr_info.raises is None or len(docstr_info.raises) == 0
    ):
        yield types_.Problem(
            docstr_node.lineno, docstr_node.col_offset, RE_RAISE_NO_EXC_IN_DOCSTR_MSG
        )
    elif all_excs and docstr_info.raises is not None:
        docstr_raises = set(docstr_info.raises)

        # Check for multiple raises sections
        if len(docstr_info.raises_sections) > 1:
            yield types_.Problem(
                docstr_node.lineno,
                docstr_node.col_offset,
                MULT_RAISES_SECTIONS_IN_DOCSTR_MSG % ",".join(docstr_info.raises_sections),
            )

        # Check for exceptions that are not raised
        yield from (
            types_.Problem(exc.lineno, exc.col_offset, EXC_NOT_IN_DOCSTR_MSG % exc.name)
            for exc in all_excs
            if exc and exc.name not in docstr_raises
        )

        # Check for exceptions in the docstring that are not raised unless function has a raises
        # without an exception
        if not has_raise_no_value:
            func_exc = set(exc.name for exc in all_excs if exc is not None)
            yield from (
                types_.Problem(docstr_node.lineno, docstr_node.col_offset, EXC_IN_DOCSTR_MSG % exc)
                for exc in sorted(docstr_raises - func_exc)
            )
