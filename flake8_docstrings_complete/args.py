"""The arguments section checks."""

from __future__ import annotations

import ast
from typing import Iterator

from . import docstring, types_
from .constants import ERROR_CODE_PREFIX, MORE_INFO_BASE

ARGS_SECTION_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}020"
ARGS_SECTION_NOT_IN_DOCSTR_MSG = (
    f"{ARGS_SECTION_NOT_IN_DOCSTR_CODE} a function/ method with arguments should have the "
    "arguments section in the docstring"
    f"{MORE_INFO_BASE}{ARGS_SECTION_NOT_IN_DOCSTR_CODE.lower()}"
)
ARGS_SECTION_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}021"
ARGS_SECTION_IN_DOCSTR_MSG = (
    f"{ARGS_SECTION_IN_DOCSTR_CODE} a function/ method without arguments should not have the "
    "arguments section in the docstring"
    f"{MORE_INFO_BASE}{ARGS_SECTION_IN_DOCSTR_CODE.lower()}"
)
MULT_ARGS_SECTIONS_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}022"
MULT_ARGS_SECTIONS_IN_DOCSTR_MSG = (
    f"{MULT_ARGS_SECTIONS_IN_DOCSTR_CODE} a docstring should only contain a single arguments "
    f"section, found %s{MORE_INFO_BASE}{MULT_ARGS_SECTIONS_IN_DOCSTR_CODE.lower()}"
)
ARG_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}023"
ARG_NOT_IN_DOCSTR_MSG = (
    f'{ARG_NOT_IN_DOCSTR_CODE} "%s" argument should be described in the docstring{MORE_INFO_BASE}'
    f"{ARG_NOT_IN_DOCSTR_CODE.lower()}"
)
ARG_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}024"
ARG_IN_DOCSTR_MSG = (
    f'{ARG_IN_DOCSTR_CODE} "%s" argument should not be described in the docstring{MORE_INFO_BASE}'
    f"{ARG_IN_DOCSTR_CODE.lower()}"
)

SKIP_ARGS = {"self", "cls"}
UNUSED_ARGS_PREFIX = "_"


def _iter_args(args: ast.arguments) -> Iterator[ast.arg]:
    """Iterate over all arguments.

    Adds vararg and kwarg to the args.

    Args:
        args: The arguments to iter over.

    Yields:
        All the arguments.
    """
    yield from (arg for arg in args.args if arg.arg not in SKIP_ARGS)
    yield from (arg for arg in args.posonlyargs if arg.arg not in SKIP_ARGS)
    yield from (arg for arg in args.kwonlyargs)
    if args.vararg:
        yield args.vararg
    if args.kwarg:
        yield args.kwarg


def check(
    docstr_info: docstring.Docstring, docstr_node: ast.Constant, args: ast.arguments
) -> Iterator[types_.Problem]:
    """Check that all function/ method arguments are described in the docstring.

    Check the function/ method has at most one args section.
    Check that all arguments of the function/ method are documented except certain arguments (like
    self).
    Check that a function/ method without arguments does not have an args section.

    Args:
        docstr_info: Information about the docstring.
        docstr_node: The docstring node.
        args: The arguments of the function.

    Yields:
        All the problems with the arguments.
    """
    all_args = list(_iter_args(args))
    all_used_args = list(arg for arg in all_args if not arg.arg.startswith(UNUSED_ARGS_PREFIX))

    # Check that args section is in docstring if function/ method has used arguments
    if all_used_args and docstr_info.args is None:
        yield types_.Problem(
            docstr_node.lineno, docstr_node.col_offset, ARGS_SECTION_NOT_IN_DOCSTR_MSG
        )
    # Check that args section is not in docstring if function/ method has no arguments
    if not all_args and docstr_info.args is not None:
        yield types_.Problem(
            docstr_node.lineno, docstr_node.col_offset, ARGS_SECTION_IN_DOCSTR_MSG
        )
    elif all_args and docstr_info.args is not None:
        docstr_args = set(docstr_info.args)

        # Check for multiple args sections
        if len(docstr_info.args_sections) > 1:
            yield types_.Problem(
                docstr_node.lineno,
                docstr_node.col_offset,
                MULT_ARGS_SECTIONS_IN_DOCSTR_MSG % ",".join(docstr_info.args_sections),
            )

        # Check for function arguments that are not in the docstring
        yield from (
            types_.Problem(arg.lineno, arg.col_offset, ARG_NOT_IN_DOCSTR_MSG % arg.arg)
            for arg in all_used_args
            if arg.arg not in docstr_args
        )

        # Check for arguments in the docstring that are not function arguments
        func_args = set(arg.arg for arg in all_args)
        yield from (
            types_.Problem(docstr_node.lineno, docstr_node.col_offset, ARG_IN_DOCSTR_MSG % arg)
            for arg in sorted(docstr_args - func_args)
        )

        # Check for empty args section
        if not all_used_args and len(docstr_info.args) == 0:
            yield types_.Problem(
                docstr_node.lineno, docstr_node.col_offset, ARGS_SECTION_IN_DOCSTR_MSG
            )
