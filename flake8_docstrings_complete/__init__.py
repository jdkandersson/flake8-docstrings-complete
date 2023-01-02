"""A linter that checks docstring include all expected descriptions."""

from __future__ import annotations

import argparse
import ast
import enum
import re
from itertools import chain
from pathlib import Path
from typing import Iterable, Iterator, NamedTuple

from flake8.options.manager import OptionManager

from . import docstring

ERROR_CODE_PREFIX = "DCO"
MORE_INFO_BASE = (
    ", more information: https://github.com/jdkandersson/flake8-docstrings-complete#fix-"
)
DOCSTR_MISSING_CODE = f"{ERROR_CODE_PREFIX}010"
DOCSTR_MISSING_MSG = (
    f"{DOCSTR_MISSING_CODE} docstring should be defined for a function/ method/ class"
    f"{MORE_INFO_BASE}{DOCSTR_MISSING_CODE.lower()}"
)
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
RETURNS_SECTION_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}030"
RETURNS_SECTION_NOT_IN_DOCSTR_MSG = (
    f"{RETURNS_SECTION_NOT_IN_DOCSTR_CODE} function/ method that returns a value should have the "
    f"returns section in the docstring{MORE_INFO_BASE}{RETURNS_SECTION_NOT_IN_DOCSTR_CODE.lower()}"
)
RETURNS_SECTION_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}031"
RETURNS_SECTION_IN_DOCSTR_MSG = (
    f"{RETURNS_SECTION_IN_DOCSTR_CODE} function/ method that does not return a value should not "
    f"have the returns section in the docstring"
    f"{MORE_INFO_BASE}{RETURNS_SECTION_IN_DOCSTR_CODE.lower()}"
)
MULT_RETURNS_SECTIONS_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}032"
MULT_RETURNS_SECTIONS_IN_DOCSTR_MSG = (
    f"{MULT_RETURNS_SECTIONS_IN_DOCSTR_CODE} a docstring should only contain a single returns "
    "section, found %s"
    f"{MORE_INFO_BASE}{MULT_RETURNS_SECTIONS_IN_DOCSTR_CODE.lower()}"
)
YIELDS_SECTION_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}040"
YIELDS_SECTION_NOT_IN_DOCSTR_MSG = (
    f"{YIELDS_SECTION_NOT_IN_DOCSTR_CODE} function/ method that yields a value should have the "
    f"yields section in the docstring{MORE_INFO_BASE}{YIELDS_SECTION_NOT_IN_DOCSTR_CODE.lower()}"
)
YIELDS_SECTION_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}041"
YIELDS_SECTION_IN_DOCSTR_MSG = (
    f"{YIELDS_SECTION_IN_DOCSTR_CODE} function/ method that does not yield a value should not "
    f"have the yields section in the docstring"
    f"{MORE_INFO_BASE}{YIELDS_SECTION_IN_DOCSTR_CODE.lower()}"
)
MULT_YIELDS_SECTIONS_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}042"
MULT_YIELDS_SECTIONS_IN_DOCSTR_MSG = (
    f"{MULT_YIELDS_SECTIONS_IN_DOCSTR_CODE} a docstring should only contain a single yields "
    "section, found %s"
    f"{MORE_INFO_BASE}{MULT_YIELDS_SECTIONS_IN_DOCSTR_CODE.lower()}"
)
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
ATTRS_SECTION_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}060"
ATTRS_SECTION_NOT_IN_DOCSTR_MSG = (
    f"{ATTRS_SECTION_NOT_IN_DOCSTR_CODE} a class with attributes should have the attributes "
    f"section in the docstring{MORE_INFO_BASE}{ATTRS_SECTION_NOT_IN_DOCSTR_CODE.lower()}"
)
ATTRS_SECTION_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}061"
ATTRS_SECTION_IN_DOCSTR_MSG = (
    f"{ATTRS_SECTION_IN_DOCSTR_CODE} a function/ method without attributes should not have the "
    f"attributes section in the docstring{MORE_INFO_BASE}{ATTRS_SECTION_IN_DOCSTR_CODE.lower()}"
)
MULT_ATTRS_SECTIONS_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}062"
MULT_ATTRS_SECTIONS_IN_DOCSTR_MSG = (
    f"{MULT_ATTRS_SECTIONS_IN_DOCSTR_CODE} a docstring should only contain a single attributes "
    f"section, found %s{MORE_INFO_BASE}{MULT_ARGS_SECTIONS_IN_DOCSTR_CODE.lower()}"
)
ATTR_NOT_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}063"
ATTR_NOT_IN_DOCSTR_MSG = (
    f'{ATTR_NOT_IN_DOCSTR_CODE} "%s" attribute should be described in the docstring'
    f"{MORE_INFO_BASE}{ATTR_NOT_IN_DOCSTR_CODE.lower()}"
)
ATTR_IN_DOCSTR_CODE = f"{ERROR_CODE_PREFIX}064"
ATTR_IN_DOCSTR_MSG = (
    f'{ATTR_IN_DOCSTR_CODE} "%s" attribute should not be described in the docstring'
    f"{MORE_INFO_BASE}{ATTR_IN_DOCSTR_CODE.lower()}"
)

TEST_FILENAME_PATTERN_ARG_NAME = "--docstrings-complete-test-filename-pattern"
TEST_FILENAME_PATTERN_DEFAULT = r"test_.*\.py"
TEST_FUNCTION_PATTERN_ARG_NAME = "--docstrings-complete-test-function-pattern"
TEST_FUNCTION_PATTERN_DEFAULT = r"test_.*"
FIXTURE_FILENAME_PATTERN_ARG_NAME = "--docstrings-complete-fixture-filename-pattern"
FIXTURE_FILENAME_PATTERN_DEFAULT = r"conftest\.py"
FIXTURE_DECORATOR_PATTERN_ARG_NAME = "--docstrings-complete-fixture-decorator-pattern"
FIXTURE_DECORATOR_PATTERN_DEFAULT = r"(^|\.)fixture$"

CLASS_SELF_CLS = {"self", "cls"}
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
    yield from (arg for arg in args.args if arg.arg not in CLASS_SELF_CLS)
    yield from (arg for arg in args.posonlyargs if arg.arg not in CLASS_SELF_CLS)
    yield from (arg for arg in args.kwonlyargs)
    if args.vararg:
        yield args.vararg
    if args.kwarg:
        yield args.kwarg


def _check_args(
    docstr_info: docstring.Docstring, docstr_node: ast.Constant, args: ast.arguments
) -> Iterator[Problem]:
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
                MULT_ARGS_SECTIONS_IN_DOCSTR_MSG % ",".join(docstr_info.args_sections),
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
            Problem(node.lineno, node.col_offset, RETURNS_SECTION_NOT_IN_DOCSTR_MSG)
            for node in return_nodes_with_value
        )

    # Check for multiple returns sections
    if return_nodes_with_value and len(docstr_info.returns_sections) > 1:
        yield Problem(
            docstr_node.lineno,
            docstr_node.col_offset,
            MULT_RETURNS_SECTIONS_IN_DOCSTR_MSG % ",".join(docstr_info.returns_sections),
        )

    # Check for returns section in docstring in function that does not return a value
    if not return_nodes_with_value and docstr_info.returns:
        yield Problem(docstr_node.lineno, docstr_node.col_offset, RETURNS_SECTION_IN_DOCSTR_MSG)


def _check_yields(
    docstr_info: docstring.Docstring,
    docstr_node: ast.Constant,
    yield_nodes: Iterable[ast.Yield | ast.YieldFrom],
) -> Iterator[Problem]:
    """Check function/ method yields section.

    Args:
        docstr_info: Information about the docstring.
        docstr_node: The docstring node.
        yield_nodes: The yield and yield from nodes of the function.

    Yields:
        All the problems with the yields section.
    """
    yield_nodes_with_value = list(node for node in yield_nodes if node.value is not None)

    # Check for yield statements with value and no yields section in docstring
    if yield_nodes_with_value and not docstr_info.yields:
        yield from (
            Problem(node.lineno, node.col_offset, YIELDS_SECTION_NOT_IN_DOCSTR_MSG)
            for node in yield_nodes_with_value
        )

    # Check for multiple yields sections
    if yield_nodes_with_value and len(docstr_info.yields_sections) > 1:
        yield Problem(
            docstr_node.lineno,
            docstr_node.col_offset,
            MULT_YIELDS_SECTIONS_IN_DOCSTR_MSG % ",".join(docstr_info.yields_sections),
        )

    # Check for yields section in docstring in function that does not yield a value
    if not yield_nodes_with_value and docstr_info.yields:
        yield Problem(docstr_node.lineno, docstr_node.col_offset, YIELDS_SECTION_IN_DOCSTR_MSG)


class Node(NamedTuple):
    """Information about a node.

    Attrs:
        name: Short description of the node.
        lineno: The line number the node is on.
        col_offset: The column of the node.
    """

    name: str
    lineno: int
    col_offset: int


def _get_exc_node(node: ast.Raise) -> Node | None:
    """Get the exception value from raise.

    Args:
        node: The raise node.

    Returns:
        The exception node.
    """
    if isinstance(node.exc, ast.Name):
        return Node(name=node.exc.id, lineno=node.exc.lineno, col_offset=node.exc.col_offset)
    if isinstance(node.exc, ast.Attribute):
        return Node(name=node.exc.attr, lineno=node.exc.lineno, col_offset=node.exc.col_offset)
    if isinstance(node.exc, ast.Call):
        if isinstance(node.exc.func, ast.Name):
            return Node(
                name=node.exc.func.id,
                lineno=node.exc.func.lineno,
                col_offset=node.exc.func.col_offset,
            )
        if isinstance(node.exc.func, ast.Attribute):
            return Node(
                name=node.exc.func.attr,
                lineno=node.exc.func.lineno,
                col_offset=node.exc.func.col_offset,
            )

    return None


def _check_raises(
    docstr_info: docstring.Docstring, docstr_node: ast.Constant, raise_nodes: Iterable[ast.Raise]
) -> Iterator[Problem]:
    """Check that all raised exceptions arguments are described in the docstring.

    Check the function/ method has at most one raises section.
    Check that all raised exceptions of the function/ method are documented.
    Check that a function/ method that doesn't raise exceptions does not have a raises section.
    Ignore raise without a value.

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
        yield Problem(docstr_node.lineno, docstr_node.col_offset, RAISES_SECTION_NOT_IN_DOCSTR_MSG)
    # Check that raises section is not in docstring if function/ method raises no exceptions
    if not all_excs and docstr_info.raises is not None:
        yield Problem(docstr_node.lineno, docstr_node.col_offset, RAISES_SECTION_IN_DOCSTR_MSG)
    # Check for empty raises section
    if (all_excs and all_raise_no_value) and (
        docstr_info.raises is None or len(docstr_info.raises) == 0
    ):
        yield Problem(docstr_node.lineno, docstr_node.col_offset, RE_RAISE_NO_EXC_IN_DOCSTR_MSG)
    elif all_excs and docstr_info.raises is not None:
        docstr_raises = set(docstr_info.raises)

        # Check for multiple raises sections
        if len(docstr_info.raises_sections) > 1:
            yield Problem(
                docstr_node.lineno,
                docstr_node.col_offset,
                MULT_RAISES_SECTIONS_IN_DOCSTR_MSG % ",".join(docstr_info.raises_sections),
            )

        # Check for exceptions that are not raised
        yield from (
            Problem(exc.lineno, exc.col_offset, EXC_NOT_IN_DOCSTR_MSG % exc.name)
            for exc in all_excs
            if exc and exc.name not in docstr_raises
        )

        # Check for exceptions in the docstring that are not raised unless function has a raises
        # without an exception
        if not has_raise_no_value:
            func_exc = set(exc.name for exc in all_excs if exc is not None)
            yield from (
                Problem(docstr_node.lineno, docstr_node.col_offset, EXC_IN_DOCSTR_MSG % exc)
                for exc in sorted(docstr_raises - func_exc)
            )


def _get_class_target_name(target: ast.expr) -> ast.Name | None:
    """Get the name of the target for an assignment on the class.

    Args:
        target: The target node of an assignment expression.

    Returns:
        The Name node of the target.
    """
    if isinstance(target, ast.Name):
        return target
    if isinstance(target, ast.Attribute):
        if isinstance(target.value, ast.Name):
            return target.value
        if isinstance(target.value, ast.Attribute):
            return _get_class_target_name(target=target.value)

    # There is no valid syntax that gets to here
    return None  # pragma: nocover


def _iter_class_attrs(
    nodes: Iterable[ast.Assign | ast.AnnAssign | ast.AugAssign],
) -> Iterator[Node]:
    """Get the node of the variable being assigned at the class level if the target is a Name.

    Args:
        nodes: The assign nodes.

    Yields:
        All the nodes of name targets of the assignment expressions.
    """
    for node in nodes:
        if isinstance(node, ast.Assign):
            target_names = filter(
                None, (_get_class_target_name(target) for target in node.targets)
            )
            yield from (
                Node(lineno=name.lineno, col_offset=name.col_offset, name=name.id)
                for name in target_names
            )
        else:
            target_name = _get_class_target_name(target=node.target)
            # No valid syntax reaches else
            if target_name is not None:  # pragma: nobranch
                yield Node(
                    lineno=target_name.lineno,
                    col_offset=target_name.col_offset,
                    name=target_name.id,
                )


def _get_method_target_node(target: ast.expr) -> Node | None:
    """Get the node of the target for an assignment in a method.

    Args:
        target: The target node of an assignment expression.

    Returns:
        The Name node of the target.
    """
    if isinstance(target, ast.Attribute):
        if isinstance(target.value, ast.Name) and target.value.id in CLASS_SELF_CLS:
            return Node(lineno=target.lineno, col_offset=target.col_offset, name=target.attr)
        # No valid syntax reaches else
        if isinstance(target.value, ast.Attribute):  # pragma: nobranch
            return _get_method_target_node(target=target.value)

    return None


def _iter_method_attrs(
    nodes: Iterable[ast.Assign | ast.AnnAssign | ast.AugAssign],
) -> Iterator[Node]:
    """Get the node of the class or instance variable being assigned in methods.

    Args:
        nodes: The assign nodes.

    Yields:
        All the nodes of name targets of the assignment expressions in methods.
    """
    for node in nodes:
        if isinstance(node, ast.Assign):
            yield from filter(None, (_get_method_target_node(target) for target in node.targets))
        if isinstance(node, (ast.AnnAssign | ast.AugAssign)):
            target_node = _get_method_target_node(node.target)
            # No valid syntax reaches else
            if target_node is not None:  # pragma: nobranch
                yield target_node


def _check_attrs(
    docstr_info: docstring.Docstring,
    docstr_node: ast.Constant,
    class_assign_nodes: Iterable[ast.Assign | ast.AnnAssign | ast.AugAssign],
    method_assign_nodes: Iterable[ast.Assign | ast.AnnAssign | ast.AugAssign],
) -> Iterator[Problem]:
    """Check that all class attributes are described in the docstring.

    Check the class has at most one attrs section.
    Check that all attributes of the class are documented.
    Check that a class without attributes does not have an attrs section.

    Args:
        docstr_info: Information about the docstring.
        docstr_node: The docstring node.
        class_assign_nodes: The attributes of the class assigned in the class.
        method_assign_nodes: The attributes of the class assigned in the methods.

    Yields:
        All the problems with the attributes.
    """
    all_targets = list(
        chain(_iter_class_attrs(class_assign_nodes), _iter_method_attrs(method_assign_nodes))
    )
    all_public_targets = list(
        target for target in all_targets if not target.name.startswith(UNUSED_ARGS_PREFIX)
    )

    # Check that attrs section is in docstring if function/ method has public attributes
    if all_public_targets and docstr_info.attrs is None:
        yield Problem(docstr_node.lineno, docstr_node.col_offset, ATTRS_SECTION_NOT_IN_DOCSTR_MSG)
    # Check that attrs section is not in docstring if class has no attributes
    if not all_targets and docstr_info.attrs is not None:
        yield Problem(docstr_node.lineno, docstr_node.col_offset, ATTRS_SECTION_IN_DOCSTR_MSG)
    elif all_targets and docstr_info.attrs is not None:
        docstr_attrs = set(docstr_info.attrs)

        # Check for multiple attrs sections
        if len(docstr_info.attrs_sections) > 1:
            yield Problem(
                docstr_node.lineno,
                docstr_node.col_offset,
                MULT_ATTRS_SECTIONS_IN_DOCSTR_MSG % ",".join(docstr_info.attrs_sections),
            )

        # Check for class attributes that are not in the docstring
        yield from (
            Problem(target.lineno, target.col_offset, ATTR_NOT_IN_DOCSTR_MSG % target.name)
            for target in all_public_targets
            if target.name not in docstr_attrs
        )

        # Check for attributes in the docstring that are not class attributes
        class_attrs = set(target.name for target in all_targets)
        yield from (
            Problem(docstr_node.lineno, docstr_node.col_offset, ATTR_IN_DOCSTR_MSG % attr)
            for attr in sorted(docstr_attrs - class_attrs)
        )

        # Check for empty attrs section
        if not all_public_targets and len(docstr_info.attrs) == 0:
            yield Problem(docstr_node.lineno, docstr_node.col_offset, ATTRS_SECTION_IN_DOCSTR_MSG)


class VisitorWithinFunction(ast.NodeVisitor):
    """Visits AST nodes within a functions but not nested functions or classes.

    Attrs:
        return_nodes: All the return nodes encountered within the function.
        yield_nodes: All the yield nodes encountered within the function.
        raise_nodes: All the raise nodes encountered within the function.
    """

    return_nodes: list[ast.Return]
    yield_nodes: list[ast.Yield | ast.YieldFrom]
    raise_nodes: list[ast.Raise]
    _visited_once: bool

    def __init__(self) -> None:
        """Construct."""
        self.return_nodes = []
        self.yield_nodes = []
        self.raise_nodes = []
        self._visited_once = False

    # The function must be called the same as the name of the node
    def visit_Return(self, node: ast.Return) -> None:  # pylint: disable=invalid-name
        """Record return node.

        Args:
            node: The return node to record.
        """
        self.return_nodes.append(node)

        # Ensure recursion continues
        self.generic_visit(node)

    # The function must be called the same as the name of the node
    def visit_Yield(self, node: ast.Yield) -> None:  # pylint: disable=invalid-name
        """Record yield node.

        Args:
            node: The yield node to record.
        """
        self.yield_nodes.append(node)

        # Ensure recursion continues
        self.generic_visit(node)

    # The function must be called the same as the name of the node
    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:  # pylint: disable=invalid-name
        """Record yield from node.

        Args:
            node: The yield from node to record.
        """
        self.yield_nodes.append(node)

        # Ensure recursion continues
        self.generic_visit(node)

    # The function must be called the same as the name of the node
    def visit_Raise(self, node: ast.Raise) -> None:  # pylint: disable=invalid-name
        """Record raise node.

        Args:
            node: The raise node to record.
        """
        self.raise_nodes.append(node)

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
    visit_FunctionDef = visit_once  # noqa: N815,DCO063
    visit_AsyncFunctionDef = visit_once  # noqa: N815,DCO063
    visit_ClassDef = visit_once  # noqa: N815,DCO063


class VisitorWithinClass(ast.NodeVisitor):
    """Visits AST nodes within a class but not nested class and functions nested within functions.

    Attrs:
        class_assign_nodes: All the return nodes encountered within the class.
        method_assign_nodes: All the return nodes encountered within the class methods.
    """

    class_assign_nodes: list[ast.Assign | ast.AnnAssign | ast.AugAssign]
    method_assign_nodes: list[ast.Assign | ast.AnnAssign | ast.AugAssign]
    _visited_once: bool
    _visited_top_level: bool

    def __init__(self) -> None:
        """Construct."""
        self.class_assign_nodes = []
        self.method_assign_nodes = []
        self._visited_once = False
        self._visited_top_level = False

    def visit_assign(self, node: ast.Assign | ast.AnnAssign | ast.AugAssign) -> None:
        """Record assign node.

        Args:
            node: The assign node to record.
        """
        if not self._visited_top_level:
            self.class_assign_nodes.append(node)
        else:
            self.method_assign_nodes.append(node)

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

    def visit_top_level(self, node: ast.AST) -> None:
        """Visit the top level node but skip any nested nodes.

        Args:
            node: The node being visited.
        """
        if not self._visited_top_level:
            self._visited_top_level = True
            self.generic_visit(node=node)
            self._visited_top_level = False

    # The functions must be called the same as the name of the node
    # Visit assign nodes
    visit_Assign = visit_assign  # noqa: N815,DCO063
    visit_AnnAssign = visit_assign  # noqa: N815,DCO063
    visit_AugAssign = visit_assign  # noqa: N815,DCO063
    # Ensure that nested functions and classes are not iterated over
    visit_FunctionDef = visit_top_level  # noqa: N815,DCO063
    visit_AsyncFunctionDef = visit_top_level  # noqa: N815,DCO063
    visit_ClassDef = visit_once  # noqa: N815,DCO063


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
        """Determine whether an expression is a fixture decorator.

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
                    Problem(lineno=node.lineno, col_offset=node.col_offset, msg=DOCSTR_MISSING_MSG)
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

                # Check yields
                self.problems.extend(
                    _check_yields(
                        docstr_info=docstr_info,
                        docstr_node=docstr_node,
                        yield_nodes=visitor_within_function.yield_nodes,
                    )
                )

                # Check raises
                self.problems.extend(
                    _check_raises(
                        docstr_info=docstr_info,
                        docstr_node=docstr_node,
                        raise_nodes=visitor_within_function.raise_nodes,
                    )
                )

        # Ensure recursion continues
        self.generic_visit(node)

    # The functions must be called the same as the name of the node
    visit_FunctionDef = visit_any_function  # noqa: N815,DCO063
    visit_AsyncFunctionDef = visit_any_function  # noqa: N815,DCO063

    # The function must be called the same as the name of the node
    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # pylint: disable=invalid-name
        """Check a class definition node.

        Args:
            node: The class definition to check.
        """
        # Check docstring is defined
        if ast.get_docstring(node) is None:
            self.problems.append(
                Problem(lineno=node.lineno, col_offset=node.col_offset, msg=DOCSTR_MISSING_MSG)
            )

        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            # Check attrs
            docstr_info = docstring.parse(value=node.body[0].value.value)
            docstr_node = node.body[0].value
            visitor_within_class = VisitorWithinClass()
            visitor_within_class.visit(node=node)
            self.problems.extend(
                _check_attrs(
                    docstr_info=docstr_info,
                    docstr_node=docstr_node,
                    class_assign_nodes=visitor_within_class.class_assign_nodes,
                    method_assign_nodes=visitor_within_class.method_assign_nodes,
                )
            )

        # Ensure recursion continues
        self.generic_visit(node)


class Plugin:
    """Checks docstring include all expected descriptions.

    Attrs:
        name: The name of the plugin.
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
