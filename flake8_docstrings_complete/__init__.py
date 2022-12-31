"""A linter that checks docstring include all expected descriptions."""

from __future__ import annotations

import argparse
import ast
import enum
import re
from pathlib import Path
from typing import Iterator, NamedTuple, Iterable

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
    f'{ARG_NOT_IN_DOCSTR_CODE} "%s" argument should be described in the docstring{MORE_INFO_BASE}'
    f"{ARG_NOT_IN_DOCSTR_CODE.lower()}"
)
ARG_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}006"
ARG_IN_DOCSTR_MSG = (
    f'{ARG_IN_DOCSTR_CODE} "%s" argument should not be described in the docstring{MORE_INFO_BASE}'
    f"{ARG_IN_DOCSTR_CODE.lower()}"
)
RETURNS_SECTION_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}007"
RETURNS_SECTION_NOT_IN_DOCSTR_MSG = (
    f"{RETURNS_SECTION_NOT_IN_DOCSTR_CODE} function/ method that returns a value should have the "
    f"returns section in the docstring{MORE_INFO_BASE}{RETURNS_SECTION_NOT_IN_DOCSTR_CODE.lower()}"
)
RETURNS_SECTION_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}008"
RETURNS_SECTION_IN_DOCSTR_MSG = (
    f"{RETURNS_SECTION_IN_DOCSTR_CODE} function/ method that does not return a value should not "
    f"have the returns section in the docstring"
    f"{MORE_INFO_BASE}{RETURNS_SECTION_IN_DOCSTR_CODE.lower()}"
)
MULT_RETURNS_SECTION_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}009"
MULT_RETURNS_SECTION_IN_DOCSTR_MSG = (
    f"{MULT_RETURNS_SECTION_IN_DOCSTR_CODE} a docstring should only contain a single returns "
    "section, found %s"
    f"{MORE_INFO_BASE}{MULT_RETURNS_SECTION_IN_DOCSTR_CODE.lower()}"
)
YIELDS_SECTION_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}010"
YIELDS_SECTION_NOT_IN_DOCSTR_MSG = (
    f"{YIELDS_SECTION_NOT_IN_DOCSTR_CODE} function/ method that yields a value should have the "
    f"yields section in the docstring{MORE_INFO_BASE}{YIELDS_SECTION_NOT_IN_DOCSTR_CODE.lower()}"
)

TEST_FILENAME_PATTERN_ARG_NAME = "--docstrings-complete-test-filename-pattern"
TEST_FILENAME_PATTERN_DEFAULT = r"test_.*\.py"
TEST_FUNCTION_PATTERN_ARG_NAME = "--docstrings-complete-test-function-pattern"
TEST_FUNCTION_PATTERN_DEFAULT = r"test_.*"
FIXTURE_FILENAME_PATTERN_ARG_NAME = "--docstrings-complete-fixture-filename-pattern"
FIXTURE_FILENAME_PATTERN_DEFAULT = r"conftest\.py"
FIXTURE_DECORATOR_PATTERN_ARG_NAME = "--docstrings-complete-fixture-decorator-pattern"
FIXTURE_DECORATOR_PATTERN_DEFAULT = r"(^|\.)fixture$"

SKIP_ARGS = {"self", "cls"}
UNUSED_ARGS_PREFIX = "_"


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


class FileType(str, enum.Enum):
    """The type of file being processed.

    Attrs:
        TEST: A file with tests.
        FIXTURE: A file with fixtures.
        DEFAULT: All other files.
    """

    TEST = "test"
    FIXTURE = "fixture"
    DEFAULT = "default"


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


def _check_args(
    docstr_info: docstring.Docstring, docstr_node: ast.Constant, args: ast.arguments
) -> Iterator[Problem]:
    """Check that all function arguments are described in the docstring.

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
        yield Problem(docstr_node.lineno, docstr_node.col_offset, ARGS_SECTION_NOT_IN_DOCSTR_MSG)
    # Check that args section is not in docstring if function/ method has no arguments
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
            for arg in all_used_args
            if arg.arg not in docstr_args
        )

        # Check for arguments in the docstring that are not function arguments
        func_args = set(arg.arg for arg in all_args)
        yield from (
            Problem(docstr_node.lineno, docstr_node.col_offset, ARG_IN_DOCSTR_MSG % arg)
            for arg in sorted(docstr_args - func_args)
        )

        # Check for empty args section
        if not all_used_args and len(docstr_info.args) == 0:
            yield Problem(docstr_node.lineno, docstr_node.col_offset, ARGS_SECTION_IN_DOCSTR_MSG)


def _check_returns(
    docstr_info: docstring.Docstring, docstr_node: ast.Constant, return_nodes: Iterable[ast.Return]
) -> Iterator[Problem]:
    """Check function/ method returns section.

    Args:
        docstr_info: Information about the docstring.
        docstr_node: The docstring node.
        return_nodes: The return nodes of the function.

    Yields:
        All the problems with the returns section.
    """
    return_nodes_with_value = list(node for node in return_nodes if node.value is not None)

    # Check for return statements with value and no returns section in docstring
    if return_nodes_with_value and not docstr_info.returns:
        yield from (
            Problem(node.lineno, node.col_offset, RETURN_NOT_IN_DOCSTR_MSG)
            for node in return_nodes_with_value
        )

    # Check for multiple returns sections
    if return_nodes_with_value and len(docstr_info.returns_sections) > 1:
        yield Problem(
            docstr_node.lineno,
            docstr_node.col_offset,
            MULT_RETURNS_SECTION_IN_DOCSTR_MSG % ",".join(docstr_info.returns_sections),
        )

    # Check for returns section in docstring in function that does not return a value
    if not return_nodes_with_value and docstr_info.returns:
        yield Problem(docstr_node.lineno, docstr_node.col_offset, RETURNS_SECTION_IN_DOCSTR_MSG)


class VisitorWithinFunction(ast.NodeVisitor):
    """Visits AST nodes within a functions but not nested functions or classes.

    Attrs:
        return_nodes: All the return nodes encountered within the function.
    """

    return_nodes: list[ast.Return]
    _visited_once: bool

    def __init__(self) -> None:
        """Construct."""
        self.return_nodes = []
        self._visited_once = False

    # The function must be called the same as the name of the node
    def visit_Return(self, node: ast.Return) -> None:  # pylint: disable=invalid-name
        """Check a function definition node.

        Args:
            node: The function definition to check.
        """
        self.return_nodes.append(node)

        # Ensure recursion continues
        self.generic_visit(node)

    def visit_once(self, node: ast.AST) -> None:
        """Visit the node once and then skip.

        Args:
            node: The node being visited.
        """
        if not self._visited_once:
            self._visited_once = True
            self.generic_visit(node=node)

    # Ensure that nested functions and classes are not iterated over
    # The functions must be called the same as the name of the node
    visit_FunctionDef = visit_once  # noqa: N815
    visit_AsyncFunctionDef = visit_once  # noqa: N815
    visit_ClassDef = visit_once  # noqa: N815


class Visitor(ast.NodeVisitor):
    """Visits AST nodes and check docstrings of functions.

    Attrs:
        problems: All the problems that were encountered.
    """

    problems: list[Problem]
    _file_type: FileType
    _test_function_pattern: str
    _fixture_decorator_pattern: str

    def __init__(
        self, file_type: FileType, test_function_pattern: str, fixture_decorator_pattern: str
    ) -> None:
        """Construct.

        Args:
            file_type: The type of file being processed.
            test_function_pattern: The pattern to match test functions with.
            fixture_decorator_pattern: The pattern to match decorators of fixture function with.
        """
        self.problems = []
        self._file_type = file_type
        self._test_function_pattern = test_function_pattern
        self._fixture_decorator_pattern = fixture_decorator_pattern

    def _is_fixture_decorator(self, node: ast.expr) -> bool:
        """Determine whether an expression is a fixture decorator

        Args:
            node: The node to check.

        Returns:
            Whether the node is a decorator fixture.
        """
        # Handle variable
        fixture_name: str | None = None
        if isinstance(node, ast.Name):
            fixture_name = node.id
        if isinstance(node, ast.Attribute):
            fixture_name = node.attr
        if fixture_name is not None:
            return (
                re.search(self._fixture_decorator_pattern, fixture_name, re.IGNORECASE) is not None
            )

        # Handle call
        if isinstance(node, ast.Call):
            return self._is_fixture_decorator(node=node.func)

        return False

    def _skip_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check whether to skip a function.

        Args:
            node: The function to check

        Returns:
            Whether to skip the function.
        """
        if self._file_type == FileType.TEST and re.match(self._test_function_pattern, node.name):
            return True

        if self._file_type in {FileType.TEST, FileType.FIXTURE}:
            return any(self._is_fixture_decorator(decorator) for decorator in node.decorator_list)

        return False

    def visit_any_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Check a function definition node.

        Args:
            node: The function definition to check.
        """
        if not self._skip_function(node=node):
            # Check docstring is defined
            if ast.get_docstring(node) is None:
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
                docstr_info = docstring.parse(value=node.body[0].value.value)
                docstr_node = node.body[0].value
                self.problems.extend(
                    _check_args(docstr_info=docstr_info, docstr_node=docstr_node, args=node.args)
                )

                # Check returns
                visitor_within_function = VisitorWithinFunction()
                visitor_within_function.visit(node=node)
                self.problems.extend(
                    _check_returns(
                        docstr_info=docstr_info,
                        docstr_node=docstr_node,
                        return_nodes=visitor_within_function.return_nodes,
                    )
                )

        # Ensure recursion continues
        self.generic_visit(node)

    # The functions must be called the same as the name of the node
    visit_FunctionDef = visit_any_function  # noqa: N815
    visit_AsyncFunctionDef = visit_any_function  # noqa: N815


class Plugin:
    """Checks docstring include all expected descriptions.

    Attrs:
        name: The name of the plugin.
        version: The version of the plugin.
    """

    name = __name__
    _test_filename_pattern: str = TEST_FILENAME_PATTERN_DEFAULT
    _test_function_pattern: str = TEST_FUNCTION_PATTERN_DEFAULT
    _fixture_filename_pattern: str = FIXTURE_FILENAME_PATTERN_DEFAULT
    _fixture_decorator_pattern: str = FIXTURE_DECORATOR_PATTERN_DEFAULT
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

    def _get_file_type(self) -> FileType:
        """Get the file type from a filename.

        Returns:
            The type of file.
        """
        if re.match(self._test_filename_pattern, self._filename) is not None:
            return FileType.TEST

        if re.match(self._fixture_filename_pattern, self._filename) is not None:
            return FileType.FIXTURE

        return FileType.DEFAULT

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
                "The pattern for the name of test functions to exclude in test files. "
                f"(Default: {TEST_FUNCTION_PATTERN_DEFAULT})"
            ),
        )
        option_manager.add_option(
            FIXTURE_FILENAME_PATTERN_ARG_NAME,
            default=FIXTURE_FILENAME_PATTERN_DEFAULT,
            parse_from_config=True,
            help=(
                "The pattern to identify fixture files. "
                f"(Default: {FIXTURE_FILENAME_PATTERN_DEFAULT})"
            ),
        )
        option_manager.add_option(
            FIXTURE_DECORATOR_PATTERN_ARG_NAME,
            default=FIXTURE_DECORATOR_PATTERN_DEFAULT,
            parse_from_config=True,
            help=(
                "The pattern for the decorator name to exclude fixture functions. "
                f"(Default: {FIXTURE_DECORATOR_PATTERN_DEFAULT})"
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
        cls._fixture_filename_pattern = (
            getattr(options, _cli_arg_name_to_attr(FIXTURE_FILENAME_PATTERN_ARG_NAME), None)
            or FIXTURE_FILENAME_PATTERN_DEFAULT
        )
        cls._fixture_decorator_pattern = (
            getattr(options, _cli_arg_name_to_attr(FIXTURE_DECORATOR_PATTERN_ARG_NAME), None)
            or FIXTURE_DECORATOR_PATTERN_DEFAULT
        )

    def run(self) -> Iterator[tuple[int, int, str, type["Plugin"]]]:
        """Lint a file.

        Yields:
            All the problems that were found.
        """
        file_type = self._get_file_type()
        visitor = Visitor(
            file_type=file_type,
            test_function_pattern=self._test_function_pattern,
            fixture_decorator_pattern=self._fixture_decorator_pattern,
        )
        visitor.visit(node=self._tree)
        yield from (
            (problem.lineno, problem.col_offset, problem.msg, type(self))
            for problem in visitor.problems
        )
