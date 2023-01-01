# flake8-docstrings-complete

Linter that checks docstrings of functions, methods and classes. It should be
used in conjunction with `pydocstyle` (or `flake8-docstrings`) as the linter
assumes that the docstrings already pass `pydocstyle` checks.

## Getting Started

```shell
python -m venv venv
source ./venv/bin/activate
pip install flake8 flake8-docstrings-complete
flake8 source.py
```

On the following code where the `foo` function has the `baz` argument which is
missing from the `Args` section in the docstring:

```Python
# source.py
def foo(bar, baz):
    """Perform foo action on bar.

    Args:
        bar: The value to perform the foo action on.
    """
```

This will produce warnings such as:

```shell
flake8 test_source.py
source.py:2:14: DCO005 "baz" argument should be described in the docstring, more information: https://github.com/jdkandersson/flake8-docstrings-complete#fix-dco005
```

This can be resolved by adding the `baz` argument to the `Args` section:

```Python
# test_source.py
def foo(bar, baz):
    """Perform foo action on bar.

    Args:
        bar: The value to perform the foo action on.
        baz: The modifier to the foo action.
    """
```

`flake8-docstrings-complete` adds the following checks to complement
`pydocstyle`:

1. If a function/ method has arguments, that the arguments section is included.
2. If a function/ method has arguments, that all function/ method arguments are
   in the argument section.
3. If an arguments section is in the function/ method docstring, the argument
   section contains no arguments the function doesn't have.
4. If a function/ method has a return statement with a value, the return value
   section is included.
5. If a function/ method has a yield statement with a value, the yield value
   section is included.
6. If a function/ method raises an exception, the raises section is included
   with a description for each exception that is raised.
7. If a class has public attributes, that the attributes section is included.
8. If a class has public attributes, that all public attributes are in the
   attributes section.
9. If an attributes section is in the class docstring, the attributes section
   contains no attributes the class doesn't have.
10. Any of the sections being checked are not present multiple times.

Note:

- `self` and `cls` are not counted as arguments.
- `test_.*` methods are skipped in `test_.*\.py` files (function and file names
  are configurable).

## Configuration

The plugin adds the following configurations to `flake8`:

- `--docstrings-complete-test-filename-pattern`: The filename pattern for test
  files. Defaults to `test_.*\.py`.
- `--docstrings-complete-test-function-pattern`: The function name pattern for
  test functions. Defaults to `test_.*`.
- `--docstrings-complete-fixture-filename-pattern`: The filename pattern for
  fixture files. Defaults to `conftest\.py`.
- `--docstrings-complete-fixture-decorator-pattern`: The decorator name pattern
  for fixture functions. Defaults to `(^|\.)fixture$`.

## Rules

A few rules have been defined to allow for selective suppression:

- `DCO001`: docstring missing on a function/ method.
- `DCO002`: function/ method has one or more arguments and the docstring does
  not have an arguments section.
- `DCO003`: function/ method with no arguments and the docstring has an
  arguments section.
- `DCO004`: function/ method with one or more arguments and the docstring has
  multiple arguments sections.
- `DCO005`: function/ method has one or more arguments not described in the
  docstring.
- `DCO006`: function/ method has one or more arguments described in the
  docstring which are not arguments of the function/ method.
- `DCO007`: function/ method that returns a value does not have the returns
  section in the docstring.
- `DCO008`: function/ method that does not return a value has the returns
  section in the docstring.
- `DCO009`: function/ method that returns a value and the docstring has
  multiple returns sections.
- `DCO010`: function/ method that yields a value does not have the yields
  section in the docstring.
- `DCO011`: function/ method that does not yield a value has the yields
  section in the docstring.
- `DCO012`: function/ method that yields a value and the docstring has
  multiple yields sections.
- `DCO013`: function/ method raises one or more exceptions and the docstring
  does not have a raises section.
- `DCO014`: function/ method that raises no exceptions and the docstring has a
  raises section.
- `DCO015`: function/ method that raises one or more exceptions and the
  docstring has multiple raises sections.
- `DCO016`: function/ method that raises one or more exceptions where one or
  more of the exceptions is not described in the docstring.
- `DCO017`: function/ method has one or more exceptions described in the
  docstring which are not raised in the function/ method.

### Fix DCO001

This linting rule is triggered by a function/ method without a docstring. For
example:

```Python
def foo():
    pass

class FooClass:
    def foo(self):
        pass
```

This example can be fixed by adding a docstring:

```Python
def foo():
    """Perform foo action."""

class FooClass:
    def foo(self):
        """Perform foo action."""
```

### Fix DCO002

This linting rule is triggered by a function/ method that has one or more
arguments with a docstring that does not have an arguments section. For
example:

```Python
def foo(bar):
    """Perform foo action."""

class FooClass:
    def foo(self, bar):
        """Perform foo action."""
```

These examples can be fixed by adding the arguments section and describing all
arguments in the arguments section:

```Python
def foo(bar):
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.
    """

def foo(bar):
    """Perform foo action.

    Arguments:
        bar: the value to perform the foo action on.
    """

def foo(bar):
    """Perform foo action.

    Parameters:
        bar: the value to perform the foo action on.
    """

class FooClass:
    def foo(self, bar):
        """Perform foo action.

        Args:
            bar: the value to perform the foo action on.
        """
```

### Fix DCO003

This linting rule is triggered by a function/ method that has no arguments with
a docstring that has an arguments section. For example:

```Python
def foo():
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.
    """

def foo():
    """Perform foo action.

    Arguments:
        bar: the value to perform the foo action on.
    """

def foo():
    """Perform foo action.

    Parameters:
        bar: the value to perform the foo action on.
    """

class FooClass:
    def foo(self):
        """Perform foo action.

        Args:
            bar: the value to perform the foo action on.
        """
```

These examples can be fixed by removing the arguments section:

```Python
def foo():
    """Perform foo action."""

class FooClass:
    def foo(self):
        """Perform foo action."""
```

### Fix DCO004

This linting rule is triggered by a function/ method that has one or more
arguments and a docstring that has multiple arguments sections. For example:

```Python
def foo(bar):
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.

    Args:
        bar: the value to perform the foo action on.
    """

def foo(bar):
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.

    Arguments:
        bar: the value to perform the foo action on.

    Parameters:
        bar: the value to perform the foo action on.
    """

class FooClass:
    def foo(self, bar):
        """Perform foo action.

        Args:
            bar: the value to perform the foo action on.

        Args:
            bar: the value to perform the foo action on.
        """
```

These examples can be fixed by removing the additional arguments sections:

```Python
def foo(bar):
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.
    """

def foo(bar):
    """Perform foo action.

    Arguments:
        bar: the value to perform the foo action on.
    """

def foo(bar):
    """Perform foo action.

    Parameters:
        bar: the value to perform the foo action on.
    """

class FooClass:
    def foo(self, bar):
        """Perform foo action.

        Args:
            bar: the value to perform the foo action on.
        """
```

### Fix DCO005

This linting rule is triggered by a function/ method that has one or more
arguments where one or more of those arguments is not described in the
docstring. For example:

```Python
def foo(bar):
    """Perform foo action.

    Args:
    """

def foo(bar, baz):
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.
    """

class FooClass:
    def foo(self, bar):
        """Perform foo action.

        Args:
        """
```

These examples can be fixed by adding the missing arguments to the arguments
section:

```Python
def foo(bar):
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.
    """

def foo(bar, baz):
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.
        baz: the modifier to the foo action.
    """

class FooClass:
    def foo(self, bar):
        """Perform foo action.

        Args:
            bar: the value to perform the foo action on.
        """
```

### Fix DCO006

This linting rule is triggered by a function/ method that has one or more
arguments and a docstring that describes one or more arguments where on or more
of the described arguments are not arguments of the function. For example:

```Python
def foo(bar):
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.
        baz: the modifier to the foo action.
    """

class FooClass:
    def foo(self, bar):
        """Perform foo action.

        Args:
            bar: the value to perform the foo action on.
            baz: the modifier to the foo action.
        """
```

These examples can be fixed by removing the arguments the function doesn't have
from the docstring:

```Python
def foo(bar):
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.
    """

class FooClass:
    def foo(self, bar):
        """Perform foo action.

        Args:
            bar: the value to perform the foo action on.
        """
```

### Fix DCO007

This linting rule is triggered by a function/ method that has at least one
return statement with a value and does not have a returns section in the
docstring. For example:

```Python
def foo():
    """Return bar."""
    return "bar"

class FooClass:
    def foo(self):
        """Return bar."""
        return "bar"
```

These examples can be fixed by adding the returns section:

```Python
def foo():
    """Return bar.

    Return:
        bar.
    """
    return "bar"

def foo():
    """Return bar.

    Returns:
        bar.
    """
    return "bar"

class FooClass:
    def foo(self):
        """Return bar.

        Returns:
            bar.
        """
        return "bar"
```

### Fix DCO008

This linting rule is triggered by a function/ method that has no return
statement with a value and has a returns section in the
docstring. For example:

```Python
def foo():
    """Return bar.

    Returns:
        bar.
    """
    pass

class FooClass:
    def foo(self):
        """Return bar.

        Returns:
            bar.
        """
        pass
```

These examples can be fixed by removing the returns section:

```Python
def foo():
    """Take foo action."""
    pass

class FooClass:
    def foo(self):
        """Take foo action."""
        pass
```

### Fix DCO009

This linting rule is triggered by a function/ method that returns a value and
has a docstring that has multiple returns sections. For example:

```Python
def foo():
    """Perform foo action.

    Returns:
        bar.

    Returns:
        bar.
    """
    return "bar"

def foo():
    """Perform foo action.

    Returns:
        bar.

    Return:
        bar.
    """
    return "bar"

class FooClass:
    def foo(self):
        """Perform foo action.

        Returns:
            bar.

        Returns:
            bar.
        """
        return "bar"
```

These examples can be fixed by removing the additional returns sections:

```Python
def foo():
    """Perform foo action.

    Returns:
        bar.
    """
    return "bar"

def foo():
    """Perform foo action.

    Returns:
        bar.
    """
    return "bar"

class FooClass:
    def foo(self):
        """Perform foo action.

        Returns:
            bar.
        """
        return "bar"
```

### Fix DCO010

This linting rule is triggered by a function/ method that has at least one
yield statement with a value or a yield from statement and does not have a
yields section in the docstring. For example:

```Python
def foo():
    """Yield bar."""
    yield "bar"

def foo():
    """Yield bar."""
    yield from ("bar",)

class FooClass:
    def foo(self):
        """Yield bar."""
        yield "bar"
```

These examples can be fixed by adding the yields section:

```Python
def foo():
    """Yield bar.

    Yield:
        bar.
    """
    yield "bar"

def foo():
    """Yield bar.

    Yields:
        bar.
    """
    yield "bar"

def foo():
    """Yield bar.

    Yields:
        bar.
    """
    yield from ("bar",)

class FooClass:
    def foo(self):
        """Yield bar.

        Yields:
            bar.
        """
        yield "bar"
```

### Fix DCO011

This linting rule is triggered by a function/ method that has no yield
statement with a value nor a yield from statement and has a yields section
in the docstring. For example:

```Python
def foo():
    """Yield bar.

    Yields:
        bar.
    """
    pass

class FooClass:
    def foo(self):
        """Yield bar.

        Yields:
            bar.
        """
        pass
```

These examples can be fixed by:

```Python
def foo():
    """Take foo action."""
    pass

class FooClass:
    def foo(self):
        """Take foo action."""
        pass
```

### Fix DCO012

This linting rule is triggered by a function/ method that yields a value and
has a docstring that has multiple yields sections. For example:

```Python
def foo():
    """Perform foo action.

    Yields:
        bar.

    Yields:
        bar.
    """
    yield "bar"

def foo():
    """Perform foo action.

    Yields:
        bar.

    Yields:
        bar.
    """
    yield from ("bar",)

def foo():
    """Perform foo action.

    Yields:
        bar.

    Yield:
        bar.
    """
    yield "bar"

class FooClass:
    def foo(self):
        """Perform foo action.

        Yields:
            bar.

        Yields:
            bar.
        """
        yield "bar"
```

These examples can be fixed by removing the additional yields sections:

```Python
def foo():
    """Perform foo action.

    Yields:
        bar.
    """
    yield "bar"

def foo():
    """Perform foo action.

    Yields:
        bar.
    """
    yield from ("bar",)

def foo():
    """Perform foo action.

    Yields:
        bar.
    """
    yield "bar"

class FooClass:
    def foo(self):
        """Perform foo action.

        Yields:
            bar.
        """
        yield "bar"
```

### Fix DCO013

This linting rule is triggered by a function/ method that raises one or more
exceptions and a docstring that does not have a raises section. For example:

```Python
def foo():
    """Perform foo action."""
    raise BarError

class FooClass:
    def foo(self):
        """Perform foo action."""
        raise BarError
```

These examples can be fixed by adding the raises section and describing all
raised exceptions in it:

```Python
def foo():
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.
    """
    raise BarError

def foo():
    """Perform foo action.

    Raise:
        BarError: the value to perform the foo action on was wrong.
    """
    raise BarError

class FooClass:
    def foo(self):
        """Perform foo action.

        Raises:
            BarError: the value to perform the foo action on was wrong.
        """
        raise BarError
```

### Fix DCO014

This linting rule is triggered by a function/ method that raises no exceptions
with a docstring that has a raises section. For example:

```Python
def foo():
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.
    """

def foo():
    """Perform foo action.

    Raise:
        BarError: the value to perform the foo action on was wrong.
    """

class FooClass:
    def foo(self):
        """Perform foo action.

        Raises:
            BarError: the value to perform the foo action on was wrong.
        """
```

These examples can be fixed by removing the raises section:

```Python
def foo():
    """Perform foo action."""

class FooClass:
    def foo(self):
        """Perform foo action."""
```

### Fix DCO015

This linting rule is triggered by a function/ method that raises one or more
exceptions with a docstring that has multiple raises sections. For example:

```Python
def foo():
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.

    Raises:
        BarError: the value to perform the foo action on was wrong.
    """
    raise BarError

def foo():
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.

    Raise:
        BarError: the value to perform the foo action on was wrong.
    """
    raise BarError

class FooClass:
    def foo(self):
        """Perform foo action.

        Raises:
            BarError: the value to perform the foo action on was wrong.

        Raises:
            BarError: the value to perform the foo action on was wrong.
        """
        raise BarError
```

These examples can be fixed by removing the additional raises sections:

```Python
def foo():
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.
    """
    raise BarError

def foo():
    """Perform foo action.

    Raise:
        BarError: the value to perform the foo action on was wrong.
    """
    raise BarError

class FooClass:
    def foo(self):
        """Perform foo action.

        Raises:
            BarError: the value to perform the foo action on was wrong.
        """
        raise BarError
```

### Fix DCO016

This linting rule is triggered by a function/ method that raises one or more
exceptions where one or more of those exceptions is not described in the
docstring. For example:

```Python
def foo():
    """Perform foo action."""
    raise BarError

def foo(bar, baz):
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.
    """
    raise BarError
    raise BazError

class FooClass:
    def foo(self):
        """Perform foo action."""
        raise BarError
```

These examples can be fixed by describing the additional exceptions in the
docstring:

```Python
def foo():
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.
    """
    raise BarError

def foo(bar, baz):
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.
        BazError: the alternate value to perform the foo action on was wrong.
    """
    raise BarError
    raise BazError

class FooClass:
    def foo(self):
        """Perform foo action.

        Raises:
            BarError: the value to perform the foo action on was wrong.
        """
        raise BarError
```

### Fix DCO017

This linting rule is triggered by a function/ method that raises one or more
exceptions and a docstring that describes one or more exceptions where on or
more of the described exceptions are not raised by the function. For example:

```Python
def foo():
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.
        BazError: the alternate value to perform the foo action on was wrong.
    """
    raise BarError

class FooClass:
    def foo(self):
        """Perform foo action.

        Raises:
            BarError: the value to perform the foo action on was wrong.
            BazError: the alternate value to perform the foo action on was wrong.
        """
        raise BarError
```

These examples can be fixed by removing the exception that is not raised from
the docstring:

```Python
def foo():
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.
    """
    raise BarError

class FooClass:
    def foo(self):
        """Perform foo action.

        Raises:
            BarError: the value to perform the foo action on was wrong.
        """
        raise BarError
```

## Docstring Examples

Examples of function/ method and class docstrings are:

```Python
def foo(bar):
    """Perform the foo actions on bar.

    Args:
        bar: the value to perform the foo actions on.

    Returns:
        bar after applying to foo action to it.

    Yields:
        All the foo actions that have been performed.

    Raises:
        FooError: an error occurred whilst performing the foo action.
    """

class Foo:
    """Foo object.

    Attrs:
        bar: the value to perform the foo actions on.
    """

    def __init__(self, bar):
        """Construct.

        Args:
            bar: the value to perform the foo actions on.
        """
        self.bar = bar
```

### Fix DCO010

This linting rule is triggered by a function/ method that has at least one
yield statement with a value and does not have a yields section in the
docstring. For example:

```Python
def foo():
    """Yield bar."""
    yield "bar"

class FooClass:
    def foo(self):
        """Yield bar."""
        yield "bar"
```

These examples can be fixed by:

```Python
def foo():
    """Yield bar.

    Yield:
        bar.
    """

def foo():
    """Yield bar.

    Yields:
        bar.
    """
    yield "bar"

class FooClass:
    def foo(self):
        """Yield bar.

        Yields:
            bar.
        """
        yield "bar"
```

## Sections

There are several alternative names for each of the sections which are captured
case-insensitive:

- arguments: `Args`, `Arguments`, `Parameters`
- return value: `Return`, `Returns`
- yield value: `Yield`, `Yields`
- raise: `Raises`
- attributes: `Attrs`, `Attributes`

Section information is extracted using the following algorithm:

1. Look for a line that has zero or more whitespace characters, followed by a
   section name (non-case-sensistive) followed by a colon.
2. Look for any sub-sections on a line which starts with zero or more
   whitespace characters followed by a word, optionally followed by whitespace
   and any characters within round brackets followed by a colon.
3. The section ends if any line with zero or more whitespace characters is
   encountered or the end of the docstring is reached.

## Future Ideas:

- Check that argument, exceptions and attributes have non-empty description.
- Check that arguments, exceptions and attributes have meaningful descriptions.
