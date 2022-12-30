"""A linter that checks docstring include all expected descriptions."""

from __future__ import annotations

import ast
from typing import NamedTuple, Iterator

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
ARG_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}002"
ARG_NOT_IN_DOCSTR_MSG = (
    f"{ARG_NOT_IN_DOCSTR_CODE} %s{MORE_INFO_BASE}{ARG_NOT_IN_DOCSTR_CODE.lower()}"
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
        elif (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstr_info = docstring.parse(value=node.body[0].value.value)

            # Check args
            docstr_args = set(docstr_info.args) if docstr_info.args else {}
            self.problems.extend(
                Problem(
                    arg.lineno,
                    arg.col_offset,
                    ARG_NOT_IN_DOCSTR_MSG % f"{arg.arg} should be described in the docstring",
                )
                for arg in node.args.args
                if arg.arg not in docstr_args
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
