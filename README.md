# flake8-docstrings-complete

Linter that checks docstrings of functions, methods and classes. It should be
used in conjuction with `pydocstyle` (or `flake8-docstrings`) as the linter
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
    """Peform foo action on bar.

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
    """Peform foo action on bar.

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

This example can be fixed by:

```Python
def foo():
    """Perform foo action."""

class FooClass:
    def foo(self):
        """Perform foo action."""
```

### Fix DCO002

This linting rule is triggered by a function/ method that has one or more
arguments and a docstring that does not have an arguments section. For example:

```Python
def foo(bar):
    """Perform foo action."""

class FooClass:
    def foo(self, bar):
        """Perform foo action."""
```

This examples can be fixed by:

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

This linting rule is triggered by a function/ method that has no arguments and
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

This examples can be fixed by:

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

This examples can be fixed by:

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
    """Perform foo action."""

def foo(bar, baz):
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.
    """

class FooClass:
    def foo(self, bar):
        """Perform foo action."""
```

This examples can be fixed by:

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

This examples can be fixed by:

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

This examples can be fixed by:

```Python
def foo():
    """Return bar.

    Return:
        bar.
    """
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
        FooError: an error occured whilst performing the foo action.
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
