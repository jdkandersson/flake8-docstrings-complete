"""Types that support execution."""

from __future__ import annotations

import enum
from typing import NamedTuple


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
