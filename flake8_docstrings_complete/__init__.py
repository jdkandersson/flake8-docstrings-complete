"""A linter that checks docstring include all expected descriptions."""

from __future__ import annotations

import ast
from typing import NamedTuple, Iterator, Iterable

import astpretty

from . import docstring

ERROR_CODE_PREFIX = "DCO"
MORE_INFO_BASE = (
    ", more information: https://github.com/jdkandersson/flake8-docstrings-complete#fix-"
)
DOCSTR_MISSING_FUNC_CODE = f"{ERROR_CODE_PREFIX}001"
DOCSTR_MISSING_FUNC_MSG = (
    f"{DOCSTR_MISSING_FUNC_CODE} docstring should be defined for a function{MORE_INFO_BASE}"
    f"{DOCSTR_MISSING_FUNC_CODE.lower()}"
)
ARGS_SECTION_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}002"
ARGS_SECTION_NOT_IN_DOCSTR_MSG = (
    f"{ARGS_SECTION_NOT_IN_DOCSTR_CODE} a function with arguments should have the arguments "
    "section in the docstring"
    f"{MORE_INFO_BASE}{ARGS_SECTION_NOT_IN_DOCSTR_CODE.lower()}"
)
ARGS_SECTION_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}003"
ARGS_SECTION_IN_DOCSTR_MSG = (
    f"{ARGS_SECTION_IN_DOCSTR_CODE} a function without arguments should not have the arguments "
    "section in the docstring"
    f"{MORE_INFO_BASE}{ARGS_SECTION_IN_DOCSTR_CODE.lower()}"
)
ARG_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}004"
ARG_NOT_IN_DOCSTR_MSG = (
    f"{ARG_NOT_IN_DOCSTR_CODE} %s should be described in the docstring{MORE_INFO_BASE}"
    f"{ARG_NOT_IN_DOCSTR_CODE.lower()}"
)
ARG_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}005"
ARG_IN_DOCSTR_MSG = (
    f"{ARG_IN_DOCSTR_CODE} %s should not be described in the docstring{MORE_INFO_BASE}"
    f"{ARG_IN_DOCSTR_CODE.lower()}"
)


class Problem(NamedTuple):
    """Represents a problem within the code.

    Attrs:
        lineno: The line number the problem occurred on
        col_offset: The column the problem occurred on
        msg: The message explaining the problem
    """

    lineno: int
    col_offset: int
    msg: str


def _check_args(
    docstr_info: docstring.Docstring,
    args: Iterable[ast.arg],
    docstr_lineno: int,
    docstr_col_offset: int,
) -> Iterator[Problem]:
    """Check that all function arguments are described in the docstring.

    Args:
        docstr_info: Information about the docstring, including all the arguments described.
        args: The arguments of the function.
        docstr_lineno: The line number the docstring starts on.
        docstr_col_offset: The column offset to the start of the docstring.

    Yields:
        All the problems with the arguments.
    """
    if args and docstr_info.args is None:
        yield Problem(docstr_lineno, docstr_col_offset, ARGS_SECTION_NOT_IN_DOCSTR_MSG)
    if not args and docstr_info.args is not None:
        yield Problem(docstr_lineno, docstr_col_offset, ARGS_SECTION_IN_DOCSTR_MSG)
    elif args and docstr_info.args is not None:
        # Check for function arguments that are not in the docstring
        docstr_args = set(docstr_info.args)
        yield from (
            Problem(arg.lineno, arg.col_offset, ARG_NOT_IN_DOCSTR_MSG % arg.arg)
            for arg in args
            if arg.arg not in docstr_args
        )

        # Check for arguments in the docstring that are not function arguments
        func_args = set(arg.arg for arg in args)
        yield from (
            Problem(docstr_lineno, docstr_col_offset, ARG_IN_DOCSTR_MSG % arg)
            for arg in sorted(docstr_args - func_args)
        )


class Visitor(ast.NodeVisitor):
    """Visits AST nodes and check docstrings of test functions.

    Attrs:
        problems: All the problems that were encountered.
    """

    problems: list[Problem]

    def __init__(self) -> None:
        """Construct."""
        self.problems = []

    # The function must be called the same as the name of the node
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # pylint: disable=invalid-name
        """Visit all FunctionDef nodes and record any problems with the node.

        Args:
            node: The FunctionDef node.
        """
        if (
            not node.body
            or not isinstance(node.body[0], ast.Expr)
            or not isinstance(node.body[0].value, ast.Constant)
            or not isinstance(node.body[0].value.value, str)
        ):
            self.problems.append(
                Problem(
                    lineno=node.lineno, col_offset=node.col_offset, msg=DOCSTR_MISSING_FUNC_MSG
                )
            )

        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstr_info = docstring.parse(value=node.body[0].value.value)

            # Check args
            self.problems.extend(
                _check_args(
                    docstr_info=docstr_info,
                    args=node.args.args,
                    docstr_lineno=node.body[0].value.lineno,
                    docstr_col_offset=node.body[0].value.col_offset,
                )
            )

            astpretty.pprint(node)

        # Ensure recursion continues
        self.generic_visit(node)


class Plugin:
    """Checks docstring include all expected descriptions.

    Attrs:
        name: The name of the plugin.
        version: The version of the plugin.
    """

    name = __name__
    _tree: ast.AST
    _filename: str

    def __init__(self, tree: ast.AST, filename: str) -> None:
        """Construct.

        Args:
            tree: The AST syntax tree for a file.
            filename: The name of the file being processed.
        """
        self._tree = tree
        self._filename = filename

    def run(self) -> Iterator[tuple[int, int, str, type["Plugin"]]]:
        """Lint a file.

        Yields:
            All the problems that were found.
        """
        visitor = Visitor()
        visitor.visit(self._tree)
        yield from (
            (problem.lineno, problem.col_offset, problem.msg, type(self))
            for problem in visitor.problems
        )
