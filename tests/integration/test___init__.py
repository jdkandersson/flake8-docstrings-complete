"""Integration tests for plugin."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from flake8_docstrings_complete import (
    DOCSTR_MISSING_CODE,
    FIXTURE_DECORATOR_PATTERN_ARG_NAME,
    FIXTURE_DECORATOR_PATTERN_DEFAULT,
    FIXTURE_FILENAME_PATTERN_ARG_NAME,
    FIXTURE_FILENAME_PATTERN_DEFAULT,
    MULT_RETURNS_SECTIONS_IN_DOCSTR_CODE,
    MULT_YIELDS_SECTIONS_IN_DOCSTR_CODE,
    RETURNS_SECTION_IN_DOCSTR_CODE,
    RETURNS_SECTION_NOT_IN_DOCSTR_CODE,
    TEST_FILENAME_PATTERN_ARG_NAME,
    TEST_FILENAME_PATTERN_DEFAULT,
    TEST_FUNCTION_PATTERN_ARG_NAME,
    TEST_FUNCTION_PATTERN_DEFAULT,
    YIELDS_SECTION_IN_DOCSTR_CODE,
    YIELDS_SECTION_NOT_IN_DOCSTR_CODE,
)
from flake8_docstrings_complete.args import (
    ARG_IN_DOCSTR_CODE,
    ARG_NOT_IN_DOCSTR_CODE,
    ARGS_SECTION_IN_DOCSTR_CODE,
    ARGS_SECTION_NOT_IN_DOCSTR_CODE,
    ARGS_SECTION_NOT_IN_DOCSTR_MSG,
    DUPLICATE_ARG_CODE,
    MULT_ARGS_SECTIONS_IN_DOCSTR_CODE,
)
from flake8_docstrings_complete.attrs import (
    ATTR_IN_DOCSTR_CODE,
    ATTR_NOT_IN_DOCSTR_CODE,
    ATTRS_SECTION_IN_DOCSTR_CODE,
    ATTRS_SECTION_NOT_IN_DOCSTR_CODE,
    DUPLICATE_ATTR_CODE,
    MULT_ATTRS_SECTIONS_IN_DOCSTR_CODE,
)
from flake8_docstrings_complete.raises import (
    DUPLICATE_EXC_CODE,
    EXC_IN_DOCSTR_CODE,
    EXC_NOT_IN_DOCSTR_CODE,
    MULT_RAISES_SECTIONS_IN_DOCSTR_CODE,
    RAISES_SECTION_IN_DOCSTR_CODE,
    RAISES_SECTION_NOT_IN_DOCSTR_CODE,
    RE_RAISE_NO_EXC_IN_DOCSTR_CODE,
)


def test_help():
    """
    given: linter
    when: the flake8 help message is generated
    then: plugin is registered with flake8
    """
    with subprocess.Popen(
        f"{sys.executable} -m flake8 --help",
        stdout=subprocess.PIPE,
        shell=True,
    ) as proc:
        stdout = proc.communicate()[0].decode(encoding="utf-8")

        assert "flake8-docstrings-complete" in stdout
        assert TEST_FILENAME_PATTERN_ARG_NAME in stdout
        assert TEST_FILENAME_PATTERN_DEFAULT in stdout
        assert TEST_FUNCTION_PATTERN_ARG_NAME in stdout
        assert TEST_FUNCTION_PATTERN_DEFAULT in stdout
        assert FIXTURE_FILENAME_PATTERN_ARG_NAME in stdout
        assert FIXTURE_FILENAME_PATTERN_DEFAULT in stdout
        assert FIXTURE_DECORATOR_PATTERN_ARG_NAME in stdout
        assert FIXTURE_DECORATOR_PATTERN_DEFAULT in stdout


def create_code_file(code: str, filename: str, base_path: Path) -> Path:
    """Create the code file with the given code.

    Args:
        code: The code to write to the file.
        filename: The name of the file to create.
        base_path: The path to create the file within

    Returns:
        The path to the code file.
    """
    (code_file := base_path / filename).write_text(f'"""Docstring."""\n\n{code}')
    return code_file


def test_fail(tmp_path: Path):
    """
    given: file with Python code that fails the linting
    when: flake8 is run against the code
    then: the process exits with non-zero code and includes the error message
    """
    code_file = create_code_file(
        '\ndef foo(arg_1):\n    """Docstring."""\n', "source.py", tmp_path
    )

    with subprocess.Popen(
        f"{sys.executable} -m flake8 {code_file}",
        stdout=subprocess.PIPE,
        shell=True,
    ) as proc:
        stdout = proc.communicate()[0].decode(encoding="utf-8")

        assert ARGS_SECTION_NOT_IN_DOCSTR_MSG in stdout
        assert proc.returncode


@pytest.mark.parametrize(
    "code, filename, extra_args",
    [
        pytest.param(
            '''
def foo():
    """Docstring."""
''',
            "source.py",
            "",
            id="default",
        ),
        pytest.param(
            '''
def _test(arg_1):
    """
    arrange: line 1
    act: line 2
    assert: line 3
    """
''',
            "_test.py",
            (
                f"{TEST_FILENAME_PATTERN_ARG_NAME} .*_test\\.py "
                f"{TEST_FUNCTION_PATTERN_ARG_NAME} _test"
            ),
            id="custom test filename and function pattern",
        ),
        pytest.param(
            '''
def custom():
    """Docstring."""


@custom
def fixture(arg_1):
    """Docstring."""
''',
            "fixture.py",
            (
                f"{FIXTURE_FILENAME_PATTERN_ARG_NAME} fixture\\.py "
                f"{FIXTURE_DECORATOR_PATTERN_ARG_NAME} custom"
            ),
            id="custom fixture filename and function pattern",
        ),
        pytest.param(
            f"""
def foo():  # noqa: {DOCSTR_MISSING_CODE}
    pass
""",
            "source.py",
            "",
            id=f"{DOCSTR_MISSING_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo(arg_1):
    """Docstring."""  # noqa: {ARGS_SECTION_NOT_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{ARGS_SECTION_NOT_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo():
    """Docstring.

    Args:
        Arguments.
    """  # noqa: {ARGS_SECTION_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{ARGS_SECTION_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo(arg_1):
    """Docstring.

    Args:
        arg_1:

    Parameters:
        arg_1:
    """  # noqa: {MULT_ARGS_SECTIONS_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{MULT_ARGS_SECTIONS_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo(arg_1):  # noqa: {ARG_NOT_IN_DOCSTR_CODE}
    """Docstring.

    Args:
        Arguments.
    """
''',
            "source.py",
            "",
            id=f"{ARG_NOT_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo(
    arg_1,
    arg2,  # noqa: {ARG_NOT_IN_DOCSTR_CODE}
):
    """Docstring.

    Args:
        arg_1:
    """
''',
            "source.py",
            "",
            id=f"{ARG_NOT_IN_DOCSTR_CODE} disabled specific arg",
        ),
        pytest.param(
            f'''
def foo(arg_1):
    """Docstring.

    Args:
        arg_1:
        arg_2:
    """  # noqa: {ARG_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{ARG_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo(arg_1):
    """Docstring.

    Args:
        arg_1:
        arg_1:
    """  # noqa: {DUPLICATE_ARG_CODE}
''',
            "source.py",
            "",
            id=f"{DUPLICATE_ARG_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo():
    """Docstring."""
    return 1  # noqa: {RETURNS_SECTION_NOT_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{RETURNS_SECTION_NOT_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo():
    """Docstring.

    Returns:
        A value.
    """  # noqa: {RETURNS_SECTION_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{RETURNS_SECTION_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo():
    """Docstring.

    Returns:
        A value.

    Return:
        A value.
    """  # noqa: {MULT_RETURNS_SECTIONS_IN_DOCSTR_CODE}
    return 1
''',
            "source.py",
            "",
            id=f"{MULT_RETURNS_SECTIONS_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo():
    """Docstring."""
    yield 1  # noqa: {YIELDS_SECTION_NOT_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{YIELDS_SECTION_NOT_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo():
    """Docstring.

    Yields:
        A value.
    """  # noqa: {YIELDS_SECTION_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{YIELDS_SECTION_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo():
    """Docstring.

    Yields:
        A value.

    Yield:
        A value.
    """  # noqa: {MULT_YIELDS_SECTIONS_IN_DOCSTR_CODE}
    yield 1
''',
            "source.py",
            "",
            id=f"{MULT_YIELDS_SECTIONS_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
class Exc1Error(Exception):
    """Docstring."""


def foo():
    """Docstring."""  # noqa: {RAISES_SECTION_NOT_IN_DOCSTR_CODE}
    raise Exc1Error
''',
            "source.py",
            "",
            id=f"{RAISES_SECTION_NOT_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo():
    """Docstring.

    Raises:
        Exc1:.
    """  # noqa: {RAISES_SECTION_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{RAISES_SECTION_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
class Exc1Error(Exception):
    """Docstring."""


def foo():
    """Docstring.

    Raises:
        Exc1Error:

    Raise:
        Exc1Error:
    """  # noqa: {MULT_RAISES_SECTIONS_IN_DOCSTR_CODE}
    raise Exc1Error
''',
            "source.py",
            "",
            id=f"{MULT_RAISES_SECTIONS_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
class Exc1Error(Exception):
    """Docstring."""


class Exc2Error(Exception):
    """Docstring."""


def foo():
    """Docstring.

    Raises:
        Exc1Error:.
    """
    raise Exc1Error
    raise Exc2Error  # noqa: {EXC_NOT_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{EXC_NOT_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
class Exc1Error(Exception):
    """Docstring."""


def foo():
    """Docstring.

    Raises:
        Exc1Error:
        Exc2Error:
    """  # noqa: {EXC_IN_DOCSTR_CODE}
    raise Exc1Error
''',
            "source.py",
            "",
            id=f"{EXC_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo():
    """Docstring.

    Raises:
    """  # noqa: {RE_RAISE_NO_EXC_IN_DOCSTR_CODE},D414
    raise
''',
            "source.py",
            "",
            id=f"{RE_RAISE_NO_EXC_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
class Exc1Error(Exception):
    """Docstring."""


def foo():
    """Docstring.

    Raises:
        Exc1Error:
        Exc1Error:
    """  # noqa: {DUPLICATE_EXC_CODE}
    raise Exc1Error
''',
            "source.py",
            "",
            id=f"{DUPLICATE_EXC_CODE} disabled",
        ),
        pytest.param(
            f'''
class Class1:
    """Docstring."""  # noqa: {ATTRS_SECTION_NOT_IN_DOCSTR_CODE}

    attr_1 = "value 1"
''',
            "source.py",
            "",
            id=f"{ATTRS_SECTION_NOT_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
class Class1:
    """Docstring.

    Attrs:
        Attributes.
    """  # noqa: {ATTRS_SECTION_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{ATTRS_SECTION_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
class Class1:
    """Docstring.

    Attrs:
        attr_1:

    Attributes:
        attr_1:
    """  # noqa: {MULT_ATTRS_SECTIONS_IN_DOCSTR_CODE}

    attr_1 = "value 1"
''',
            "source.py",
            "",
            id=f"{MULT_ATTRS_SECTIONS_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
class Class1:
    """Docstring.

    Attrs:
        Attributes.
    """

    attr_1 = "value 1"  # noqa: {ATTR_NOT_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{ATTR_NOT_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
class Class1:
    """Docstring.

    Attrs:
        attr_1:
    """

    attr_1 = "value 1"
    attr_2 = "value 2"  # noqa: {ATTR_NOT_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{ATTR_NOT_IN_DOCSTR_CODE} disabled specific arg",
        ),
        pytest.param(
            f'''
class Class1:
    """Docstring.

    Attrs:
        attr_1:
        attr_2:
    """  # noqa: {ATTR_IN_DOCSTR_CODE}

    attr_1 = "value 1"
''',
            "source.py",
            "",
            id=f"{ATTR_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
class Class1:
    """Docstring.

    Attrs:
        attr_1:
        attr_1:
    """  # noqa: {DUPLICATE_ATTR_CODE}

    attr_1 = "value 1"
''',
            "source.py",
            "",
            id=f"{DUPLICATE_ATTR_CODE} disabled",
        ),
    ],
)
def test_pass(code: str, filename: str, extra_args: str, tmp_path: Path):
    """
    given: file with Python code that passes the linting
    when: flake8 is run against the code
    then: the process exits with zero code and empty stdout
    """
    code_file = create_code_file(code, filename, tmp_path)
    (config_file := tmp_path / ".flake8").touch()

    with subprocess.Popen(
        (
            f"{sys.executable} -m flake8 {code_file} {extra_args} --ignore D205,D400,D103 "
            f"--config {config_file}"
        ),
        stdout=subprocess.PIPE,
        shell=True,
    ) as proc:
        stdout = proc.communicate()[0].decode(encoding="utf-8")

        assert not stdout, stdout
        assert not proc.returncode


def test_self():
    """
    given: working linter
    when: flake8 is run against the source and tests of the linter
    then: the process exits with zero code and empty stdout
    """
    with subprocess.Popen(
        f"{sys.executable} -m flake8 flake8_docstrings_complete/ tests/ --ignore D205,D400,D103",
        stdout=subprocess.PIPE,
        shell=True,
    ) as proc:
        stdout = proc.communicate()[0].decode(encoding="utf-8")

        assert not stdout, stdout
        assert not proc.returncode
