"""The arguments section checks."""

from __future__ import annotations

import ast
from itertools import chain
from typing import Iterable, Iterator

from . import docstring, types_
from .constants import ERROR_CODE_PREFIX, MORE_INFO_BASE

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
    f"section, found %s{MORE_INFO_BASE}{MULT_ATTRS_SECTIONS_IN_DOCSTR_CODE.lower()}"
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

CLASS_SELF_CLS = {"self", "cls"}
PRIVATE_ATTR_PREFIX = "_"


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
) -> Iterator[types_.Node]:
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
                types_.Node(lineno=name.lineno, col_offset=name.col_offset, name=name.id)
                for name in target_names
            )
        else:
            target_name = _get_class_target_name(target=node.target)
            # No valid syntax reaches else
            if target_name is not None:  # pragma: nobranch
                yield types_.Node(
                    lineno=target_name.lineno,
                    col_offset=target_name.col_offset,
                    name=target_name.id,
                )


def _get_method_target_node(target: ast.expr) -> types_.Node | None:
    """Get the node of the target for an assignment in a method.

    Args:
        target: The target node of an assignment expression.

    Returns:
        The Name node of the target.
    """
    if isinstance(target, ast.Attribute):
        if isinstance(target.value, ast.Name) and target.value.id in CLASS_SELF_CLS:
            return types_.Node(
                lineno=target.lineno, col_offset=target.col_offset, name=target.attr
            )
        # No valid syntax reaches else
        if isinstance(target.value, ast.Attribute):  # pragma: nobranch
            return _get_method_target_node(target=target.value)

    return None


def _iter_method_attrs(
    nodes: Iterable[ast.Assign | ast.AnnAssign | ast.AugAssign],
) -> Iterator[types_.Node]:
    """Get the node of the class or instance variable being assigned in methods.

    Args:
        nodes: The assign nodes.

    Yields:
        All the nodes of name targets of the assignment expressions in methods.
    """
    for node in nodes:
        if isinstance(node, ast.Assign):
            yield from filter(None, (_get_method_target_node(target) for target in node.targets))
        else:
            target_node = _get_method_target_node(node.target)
            # No valid syntax reaches else
            if target_node is not None:  # pragma: nobranch
                yield target_node


def check(
    docstr_info: docstring.Docstring,
    docstr_node: ast.Constant,
    class_assign_nodes: Iterable[ast.Assign | ast.AnnAssign | ast.AugAssign],
    method_assign_nodes: Iterable[ast.Assign | ast.AnnAssign | ast.AugAssign],
) -> Iterator[types_.Problem]:
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
        target for target in all_targets if not target.name.startswith(PRIVATE_ATTR_PREFIX)
    )

    # Check that attrs section is in docstring if function/ method has public attributes
    if all_public_targets and docstr_info.attrs is None:
        yield types_.Problem(
            docstr_node.lineno, docstr_node.col_offset, ATTRS_SECTION_NOT_IN_DOCSTR_MSG
        )
    # Check that attrs section is not in docstring if class has no attributes
    if not all_targets and docstr_info.attrs is not None:
        yield types_.Problem(
            docstr_node.lineno, docstr_node.col_offset, ATTRS_SECTION_IN_DOCSTR_MSG
        )
    elif all_targets and docstr_info.attrs is not None:
        docstr_attrs = set(docstr_info.attrs)

        # Check for multiple attrs sections
        if len(docstr_info.attrs_sections) > 1:
            yield types_.Problem(
                docstr_node.lineno,
                docstr_node.col_offset,
                MULT_ATTRS_SECTIONS_IN_DOCSTR_MSG % ",".join(docstr_info.attrs_sections),
            )

        # Check for class attributes that are not in the docstring
        yield from (
            types_.Problem(target.lineno, target.col_offset, ATTR_NOT_IN_DOCSTR_MSG % target.name)
            for target in all_public_targets
            if target.name not in docstr_attrs
        )

        # Check for attributes in the docstring that are not class attributes
        class_attrs = set(target.name for target in all_targets)
        yield from (
            types_.Problem(docstr_node.lineno, docstr_node.col_offset, ATTR_IN_DOCSTR_MSG % attr)
            for attr in sorted(docstr_attrs - class_attrs)
        )

        # Check for empty attrs section
        if not all_public_targets and len(docstr_info.attrs) == 0:
            yield types_.Problem(
                docstr_node.lineno, docstr_node.col_offset, ATTRS_SECTION_IN_DOCSTR_MSG
            )


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
