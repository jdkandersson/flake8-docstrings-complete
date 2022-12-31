"""Integration tests for plugin."""

import subprocess
import sys
from pathlib import Path

import pytest

from flake8_docstrings_complete import (
    ARG_IN_DOCSTR_CODE,
    ARG_NOT_IN_DOCSTR_CODE,
    ARGS_SECTION_IN_DOCSTR_CODE,
    ARGS_SECTION_NOT_IN_DOCSTR_CODE,
    ARGS_SECTION_NOT_IN_DOCSTR_MSG,
    DOCSTR_MISSING_FUNC_CODE,
    MULT_ARGS_SECTION_IN_DOCSTR_CODE,
    TEST_FILENAME_PATTERN_ARG_NAME,
    TEST_FILENAME_PATTERN_DEFAULT,
    TEST_FUNCTION_PATTERN_ARG_NAME,
    TEST_FUNCTION_PATTERN_DEFAULT,
    FIXTURE_FILENAME_PATTERN_ARG_NAME,
    FIXTURE_FILENAME_PATTERN_DEFAULT,
    FIXTURE_DECORATOR_PATTERN_ARG_NAME,
    FIXTURE_DECORATOR_PATTERN_DEFAULT,
    RETURN_NOT_IN_DOCSTR_CODE,
    RETURN_IN_DOCSTR_CODE,
    MULT_RETURNS_SECTION_IN_DOCSTR_CODE,
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
def foo():  # noqa: {DOCSTR_MISSING_FUNC_CODE}
    pass
""",
            "source.py",
            "",
            id=f"{DOCSTR_MISSING_FUNC_CODE} disabled",
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
    """  # noqa: {MULT_ARGS_SECTION_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{MULT_ARGS_SECTION_IN_DOCSTR_CODE} disabled",
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
def foo():
    """Docstring."""
    return 1  # noqa: {RETURN_NOT_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{RETURN_NOT_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo():
    """Docstring.

    Returns:
        A value.
    """  # noqa: {RETURN_IN_DOCSTR_CODE}
''',
            "source.py",
            "",
            id=f"{RETURN_IN_DOCSTR_CODE} disabled",
        ),
        pytest.param(
            f'''
def foo():
    """Docstring.

    Returns:
        A value.

    Return:
        A value.
    """  # noqa: {MULT_RETURNS_SECTION_IN_DOCSTR_CODE}
    return 1
''',
            "source.py",
            "",
            id=f"{MULT_RETURNS_SECTION_IN_DOCSTR_CODE} disabled",
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
