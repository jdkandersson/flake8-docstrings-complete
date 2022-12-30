"""A linter that checks docstring include all expected descriptions."""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path
from typing import Iterator, NamedTuple

from flake8.options.manager import OptionManager

from . import docstring

ERROR_CODE_PREFIX = "DCO"
MORE_INFO_BASE = (
    ", more information: https://github.com/jdkandersson/flake8-docstrings-complete#fix-"
)
DOCSTR_MISSING_FUNC_CODE = f"{ERROR_CODE_PREFIX}001"
DOCSTR_MISSING_FUNC_MSG = (
    f"{DOCSTR_MISSING_FUNC_CODE} docstring should be defined for a function/ method"
    f"{MORE_INFO_BASE}{DOCSTR_MISSING_FUNC_CODE.lower()}"
)
ARGS_SECTION_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}002"
ARGS_SECTION_NOT_IN_DOCSTR_MSG = (
    f"{ARGS_SECTION_NOT_IN_DOCSTR_CODE} a function/ method with arguments should have the "
    "arguments section in the docstring"
    f"{MORE_INFO_BASE}{ARGS_SECTION_NOT_IN_DOCSTR_CODE.lower()}"
)
ARGS_SECTION_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}003"
ARGS_SECTION_IN_DOCSTR_MSG = (
    f"{ARGS_SECTION_IN_DOCSTR_CODE} a function/ method without arguments should not have the "
    "arguments section in the docstring"
    f"{MORE_INFO_BASE}{ARGS_SECTION_IN_DOCSTR_CODE.lower()}"
)
MULT_ARGS_SECTION_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}004"
MULT_ARGS_SECTION_IN_DOCSTR_MSG = (
    f"{MULT_ARGS_SECTION_IN_DOCSTR_CODE} a docstring should only contain a single args section, "
    "found %s"
    f"{MORE_INFO_BASE}{MULT_ARGS_SECTION_IN_DOCSTR_CODE.lower()}"
)
ARG_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}005"
ARG_NOT_IN_DOCSTR_MSG = (
    f"{ARG_NOT_IN_DOCSTR_CODE} %s should be described in the docstring{MORE_INFO_BASE}"
    f"{ARG_NOT_IN_DOCSTR_CODE.lower()}"
)
ARG_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}006"
ARG_IN_DOCSTR_MSG = (
    f"{ARG_IN_DOCSTR_CODE} %s should not be described in the docstring{MORE_INFO_BASE}"
    f"{ARG_IN_DOCSTR_CODE.lower()}"
)
TEST_FILENAME_PATTERN_ARG_NAME = "--docstrings-complete-test-filename-pattern"
TEST_FILENAME_PATTERN_DEFAULT = r"test_.*\.py"
TEST_FUNCTION_PATTERN_ARG_NAME = "--docstrings-complete-test-function-pattern"
TEST_FUNCTION_PATTERN_DEFAULT = r"test_.*"
SKIPPED_ARGS = {"self", "cls"}


# Helper function for option management, tested in integration tests
def _cli_arg_name_to_attr(cli_arg_name: str) -> str:
    """Transform CLI argument name to the attribute name on the namespace.

    Args:
        cli_arg_name: The CLI argument name to transform.

    Returns:
        The namespace name for the argument.
    """
    return cli_arg_name.lstrip("-").replace("-", "_")  # pragma: nocover


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


def _iter_args(args: ast.arguments) -> Iterator[ast.arg]:
    """Iterate over all arguments.

    Adds vararg and kwarg to the args.

    Args:
        args: The arguments to iter over.

    Yields:
        All the arguments.
    """
    yield from (arg for arg in args.args if arg.arg not in SKIPPED_ARGS)
    yield from (arg for arg in args.posonlyargs if arg.arg not in SKIPPED_ARGS)
    yield from (arg for arg in args.kwonlyargs)
    if args.vararg:
        yield args.vararg
    if args.kwarg:
        yield args.kwarg


def _check_args(docstr_node: ast.Constant, args: ast.arguments) -> Iterator[Problem]:
    """Check that all function arguments are described in the docstring.

    Assume that docstr_node is a str constant.

    Args:
        docstr_node: The docstring node.
        args: The arguments of the function.

    Yields:
        All the problems with the arguments.
    """
    assert isinstance(docstr_node.value, str)
    docstr_info = docstring.parse(value=docstr_node.value)
    all_args = list(_iter_args(args))

    if all_args and docstr_info.args is None:
        yield Problem(docstr_node.lineno, docstr_node.col_offset, ARGS_SECTION_NOT_IN_DOCSTR_MSG)
    if not all_args and docstr_info.args is not None:
        yield Problem(docstr_node.lineno, docstr_node.col_offset, ARGS_SECTION_IN_DOCSTR_MSG)
    elif all_args and docstr_info.args is not None:
        docstr_args = set(docstr_info.args)

        # Check for multiple args sections
        if len(docstr_info.args_sections) > 1:
            yield Problem(
                docstr_node.lineno,
                docstr_node.col_offset,
                MULT_ARGS_SECTION_IN_DOCSTR_MSG % ",".join(docstr_info.args_sections),
            )

        # Check for function arguments that are not in the docstring
        yield from (
            Problem(arg.lineno, arg.col_offset, ARG_NOT_IN_DOCSTR_MSG % arg.arg)
            for arg in all_args
            if arg.arg not in docstr_args
        )

        # Check for arguments in the docstring that are not function arguments
        func_args = set(arg.arg for arg in all_args)
        yield from (
            Problem(docstr_node.lineno, docstr_node.col_offset, ARG_IN_DOCSTR_MSG % arg)
            for arg in sorted(docstr_args - func_args)
        )


class Visitor(ast.NodeVisitor):
    """Visits AST nodes and check docstrings of test functions.

    Attrs:
        problems: All the problems that were encountered.
    """

    problems: list[Problem]
    _test_file: bool
    _test_function_pattern: str

    def __init__(self, test_file: bool, test_function_pattern: str) -> None:
        """Construct.

        Args:
            test_file: Whether to enable function pattern checks. Usually
                enabled for test files.
            test_function_pattern: The pattern to match test functions with.
        """
        self.problems = []
        self._test_file = test_file
        self._test_function_pattern = test_function_pattern

    def check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Check a function definition node.

        Args:
            node: The function definition to check.
        """
        if not self._test_file or not re.match(self._test_function_pattern, node.name):
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
                # Check args
                self.problems.extend(_check_args(docstr_node=node.body[0].value, args=node.args))

        # Ensure recursion continues
        self.generic_visit(node)

    # The function must be called the same as the name of the node
    visit_FunctionDef = check_function  # noqa: N815
    visit_AsyncFunctionDef = check_function  # noqa: N815


class Plugin:
    """Checks docstring include all expected descriptions.

    Attrs:
        name: The name of the plugin.
        version: The version of the plugin.
    """

    name = __name__
    _test_filename_pattern: str = TEST_FILENAME_PATTERN_DEFAULT
    _test_function_pattern: str = TEST_FUNCTION_PATTERN_DEFAULT
    _tree: ast.AST
    _filename: str

    def __init__(self, tree: ast.AST, filename: str) -> None:
        """Construct.

        Args:
            tree: The AST syntax tree for a file.
            filename: The name of the file being processed.
        """
        self._tree = tree
        self._filename = Path(filename).name

    # No coverage since this only occurs from the command line
    @staticmethod
    def add_options(option_manager: OptionManager) -> None:  # pragma: nocover
        """Add additional options to flake8.

        Args:
            option_manager: The flake8 OptionManager.
        """
        option_manager.add_option(
            TEST_FILENAME_PATTERN_ARG_NAME,
            default=TEST_FILENAME_PATTERN_DEFAULT,
            parse_from_config=True,
            help=(
                "The pattern to identify test files. "
                f"(Default: {TEST_FILENAME_PATTERN_DEFAULT})"
            ),
        )
        option_manager.add_option(
            TEST_FUNCTION_PATTERN_ARG_NAME,
            default=TEST_FUNCTION_PATTERN_DEFAULT,
            parse_from_config=True,
            help=(
                "The pattern test functions to exclude in test files. "
                f"(Default: {TEST_FUNCTION_PATTERN_DEFAULT})"
            ),
        )

    # No coverage since this only occurs from the command line
    @classmethod
    def parse_options(cls, options: argparse.Namespace) -> None:  # pragma: nocover
        """Record the value of the options.
        Args:
            options: The options passed to flake8.
        """
        cls._test_filename_pattern = (
            getattr(options, _cli_arg_name_to_attr(TEST_FILENAME_PATTERN_ARG_NAME), None)
            or TEST_FILENAME_PATTERN_DEFAULT
        )
        cls._test_function_pattern = (
            getattr(options, _cli_arg_name_to_attr(TEST_FUNCTION_PATTERN_ARG_NAME), None)
            or TEST_FUNCTION_PATTERN_DEFAULT
        )

    def run(self) -> Iterator[tuple[int, int, str, type["Plugin"]]]:
        """Lint a file.

        Yields:
            All the problems that were found.
        """
        visitor = Visitor(
            re.match(self._test_filename_pattern, self._filename) is not None,
            self._test_function_pattern,
        )
        visitor.visit(self._tree)
        yield from (
            (problem.lineno, problem.col_offset, problem.msg, type(self))
            for problem in visitor.problems
        )
