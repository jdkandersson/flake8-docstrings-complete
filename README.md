# flake8-docstrings-complete

Linter that checks docstrings of functions, methods and classes. It should be
used in conjunction with `pydocstyle` (or `flake8-docstrings`) as the linter
assumes that the docstrings already pass `pydocstyle` checks. This
[blog post](https://jdkandersson.com/2023/01/07/writing-great-docstrings-in-python/)
discusses how to write great docstrings and the motivation for this linter!

## Getting Started

```shell
python -m venv venv
source ./venv/bin/activate
pip install flake8 flake8-docstrings flake8-docstrings-complete
flake8 source.py
```

On the following code where the `foo` function has the `bar` and `baz`
arguments where the `baz` argument is missing from the `Args` section in the
docstring:

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
source.py:2:14: DCO023 "baz" argument should be described in the docstring, more information: https://github.com/jdkandersson/flake8-docstrings-complete#fix-dco023
```

This can be resolved by adding the `baz` argument to the `Args` section:

```Python
# source.py
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
   section contains no arguments the function/ method doesn't have.
4. Function/ method arguments are only documented once.
5. If a function/ method has a return statement with a value, the return value
   section is included.
6. If a function/ method has a yield statement with a value, the yield value
   section is included.
7. If a function/ method raises an exception, the raises section is included
   with a description for each exception that is raised.
8. Each raised exception is only described once.
9. If a class has public attributes, that the attributes section is included.
10. If a class has public attributes, that all public attributes are in the
   attributes section.
11. If an attributes section is in the class docstring, the attributes section
   contains no attributes the class doesn't have.
12. Class attributes are only documented once.
13. Any of the sections being checked are not present multiple times.

Note:

- `self` and `cls` are not counted as arguments.
- `test_.*` methods are skipped in `test_.*\.py` files (function and file names
  are configurable).
- functions with a `@fixture` et al dectorator in `conftest.py` and
  `test_.*\.py` files are skipped (function and fixture file names are
  configurable)

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

- `DCO010`: docstring missing on a function/ method/ class.
- `DCO020`: function/ method has one or more arguments and the docstring does
  not have an arguments section.
- `DCO021`: function/ method with no arguments and the docstring has an
  arguments section.
- `DCO022`: function/ method with one or more arguments and the docstring has
  multiple arguments sections.
- `DCO023`: function/ method has one or more arguments not described in the
  docstring.
- `DCO024`: function/ method has one or more arguments described in the
  docstring which are not arguments of the function/ method.
- `DCO025`: function/ method has one or more arguments described in the
  docstring multiple times.
- `DCO030`: function/ method that returns a value does not have the returns
  section in the docstring.
- `DCO031`: function/ method that does not return a value has the returns
  section in the docstring.
- `DCO032`: function/ method that returns a value and the docstring has
  multiple returns sections.
- `DCO040`: function/ method that yields a value does not have the yields
  section in the docstring.
- `DCO041`: function/ method that does not yield a value has the yields
  section in the docstring.
- `DCO042`: function/ method that yields a value and the docstring has
  multiple yields sections.
- `DCO050`: function/ method raises one or more exceptions and the docstring
  does not have a raises section.
- `DCO051`: function/ method that raises no exceptions and the docstring has a
  raises section.
- `DCO052`: function/ method that raises one or more exceptions and the
  docstring has multiple raises sections.
- `DCO053`: function/ method that raises one or more exceptions where one or
  more of the exceptions is not described in the docstring.
- `DCO054`: function/ method has one or more exceptions described in the
  docstring which are not raised in the function/ method.
- `DCO055`: function/ method that has a raise without an exception has an empty
  raises section in the docstring.
- `DCO056`: function/ method has one or more exceptions described in the
  docstring multiple times.
- `DCO060`: class has one or more public attributes and the docstring does not
  have an attributes section.
- `DCO061`: class with no attributes and the docstring has an attributes
  section.
- `DCO062`: class with one or more attributes and the docstring has multiple
  attributes sections.
- `DCO063`: class has one or more public attributes not described in the
  docstring.
- `DCO064`: class has one or more attributes described in the docstring which
  are not attributes of the class.
- `DCO065`: class has one or more attributes described in the docstring
  multiple times.

### Fix DCO010

This linting rule is triggered by a function/ method/ class without a
docstring. For example:

```Python
def foo():
    pass

class FooClass:
    def foo(self):
        """Perform foo action."""
        pass

class FooClass:
    """Perform foo action."""
    def foo(self):
        pass
```

This example can be fixed by adding a docstring:

```Python
def foo():
    """Perform foo action."""

class FooClass:
    """Perform foo action."""
    def foo(self):
        """Perform foo action."""
```

### Fix DCO020

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

### Fix DCO021

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

### Fix DCO022

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

### Fix DCO023

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

### Fix DCO024

This linting rule is triggered by a function/ method that has one or more
arguments and a docstring that describes one or more arguments where on or more
of the described arguments are not arguments of the function/ method. For
example:

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

These examples can be fixed by removing the arguments the function/ method
doesn't have from the docstring:

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

### Fix DCO025

This linting rule is triggered by a function/ method that has one or more
arguments and a docstring that describes one or more arguments where on or more
of the described arguments are described multiple times. For example:

```Python
def foo(bar):
    """Perform foo action.

    Args:
        bar: the value to perform the foo action on.
        bar: the value to perform the foo action on.
    """

class FooClass:
    def foo(self, bar):
        """Perform foo action.

        Args:
            bar: the value to perform the foo action on.
            bar: the value to perform the foo action on.
        """
```

These examples can be fixed by removing the duplicate arguments from the docstring:

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

### Fix DCO030

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

### Fix DCO031

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

### Fix DCO032

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

### Fix DCO040

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

### Fix DCO041

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

### Fix DCO042

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

### Fix DCO050

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

### Fix DCO051

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

### Fix DCO052

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

### Fix DCO053

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

### Fix DCO054

This linting rule is triggered by a function/ method that raises one or more
exceptions and a docstring that describes one or more exceptions where on or
more of the described exceptions are not raised by the function/ method. For
example:

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

### Fix DCO055

This linting rule is triggered by a function/ method that has a `raise`
statement without an exception (typically re-raising exceptions) and the raises
section is not included or is empty. For example:

```Python
def foo():
    """Perform foo action."""
    try:
        bar()
    except BarError:
        raise

def foo():
    """Perform foo action.

    Raises:
    """
    try:
        bar()
    except BarError:
        raise

class FooClass:
    def foo(self):
        """Perform foo action."""
        try:
            bar()
        except BarError:
            raise
```

These examples can be fixed by describing at least one exception in the raises
section:

```Python
def foo():
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.
    """
    try:
        bar()
    except BarError:
        raise

def foo():
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.
    """
    try:
        bar()
    except BarError:
        raise

class FooClass:
    def foo(self):
        """Perform foo action.

        Raises:
            BarError: the value to perform the foo action on was wrong.
        """
        try:
            bar()
        except BarError:
            raise
```

### Fix DCO056

This linting rule is triggered by a function/ method that raises one or more
exceptions and a docstring that describes one or more exceptions where on or
more of the described exceptions are described multiple times. For example:

```Python
def foo():
    """Perform foo action.

    Raises:
        BarError: the value to perform the foo action on was wrong.
        BarError: the value to perform the foo action on was wrong.
    """
    raise BarError

class FooClass:
    def foo(self):
        """Perform foo action.

        Raises:
            BarError: the value to perform the foo action on was wrong.
            BarError: the value to perform the foo action on was wrong.
        """
        raise BarError
```

These examples can be fixed by removing the duplicate descriptions from the
docstring:

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

### Fix DCO060

This linting rule is triggered by a class that has one or more public
attributes with a docstring that does not have an attributes section. For
example:

```Python
class FooClass:
    """Perform foo action."""
    bar = "bar"

class FooClass:
    """Perform foo action."""

    def __init__(self):
        self.bar = "bar"

class FooClass:
    """Perform foo action."""

    def bar(self):
        self.baz = "baz"

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """
    bar = "bar"
    baz = "baz"
```

These examples can be fixed by adding the attributes section and describing all
attributes in the attributes section:

```Python
class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """
    bar = "bar"

class FooClass:
    """Perform foo action.

    Attributes:
        bar: The value to perform the foo action on.
    """
    bar = "bar"

class FooClass:
    """Perform foo action.

    Attributes:
        bar: The value to perform the foo action on.
    """

    def __init__(self):
        self.bar = "bar"

class FooClass:
    """Perform foo action.

    Attributes:
        baz: The value to perform the foo action on.
    """

    def bar(self):
        self.baz = "baz"

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
        baz: The alternate value to perform the foo action on.
    """
    bar = "bar"
    baz = "baz"
```

### Fix DCO061

This linting rule is triggered by a class that has no attributes with a
docstring that has an attributes section. For example:

```Python
class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """

class FooClass:
    """Perform foo action.

    Attributes:
        bar: The value to perform the foo action on.
    """

class FooClass:
    """Perform foo action.

    Attributes:
    """

    def __init__(self):
        self._bar = "bar"
```

These examples can be fixed by removing the attributes section:

```Python
class FooClass:
    """Perform foo action."""

class FooClass:
    """Perform foo action."""

    def __init__(self):
        self._bar = "bar"
```

### Fix DCO062

This linting rule is triggered by a class that has one or more attributes and
a docstring that has multiple attributes sections. For example:

```Python
class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.

    Attrs:
        bar: The value to perform the foo action on.
    """
    bar = "bar"

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.

    Attributes:
        bar: The value to perform the foo action on.
    """
    bar = "bar"
```

These examples can be fixed by removing the additional attributes sections:

```Python
class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """
    bar = "bar"

class FooClass:
    """Perform foo action.

    Attributes:
        bar: The value to perform the foo action on.
    """
    bar = "bar"
```

### Fix DCO063

This linting rule is triggered by a class that has one or more public
attributes where one or more of those public attributes is not described in the
docstring. For example:

```Python
class FooClass:
    """Perform foo action."""
    bar = "bar"

class FooClass:
    """Perform foo action.

    Attrs:
    """

    @property
    def bar(self):
        return "bar"

class FooClass:
    """Perform foo action.

    Attrs:
    """

    @functools.cached_property
    def bar(self):
        return "bar"

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """
    bar = "bar"
    baz = "baz"
```

These examples can be fixed by adding the missing attributes to the attributes
section:

```Python
class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """
    bar = "bar"

class FooClass:
    """Perform foo action.

    Attributes:
        bar: The value to perform the foo action on.
    """
    bar = "bar"

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """

    @property
    def bar(self):
        return "bar"

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """

    @functools.cached_property
    def bar(self):
        return "bar"

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
        baz: The alternate value to perform the foo action on.
    """
    bar = "bar"
    baz = "baz"
```

### Fix DCO064

This linting rule is triggered by a class that has one or more attributes and a
docstring that describes one or more attributes where on or more
of the described attributes are not attributes of the class. For example:

```Python
class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """

class FooClass:
    """Perform foo action.

    Attrs:
        _bar: The value to perform the foo action on.
    """

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
        baz: The alternate value to perform the foo action on.
    """
    bar = "bar"
```

These examples can be fixed by removing the attributes the class doesn't have
from the docstring:

```Python
class FooClass:
    """Perform foo action."""

class FooClass:
    """Perform foo action."""

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """
    bar = "bar"

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """

    def __init__(self):
        """Construct."""
        self.bar = "bar"
```

### Fix DCO065

This linting rule is triggered by a class that has one or more attributes and a
docstring that describes one or more attributes where on or more
of the described attributes are described multiple times. For example:

```Python
class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
        bar: The value to perform the foo action on.
    """

    bar = "bar"

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
        bar: The value to perform the foo action on.
    """

    def __init__(self):
        """Construct."""
        self.bar = "bar"
```

These examples can be fixed by removing the duplicate descriptions from the
docstring:

```Python
class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """

    bar = "bar"

class FooClass:
    """Perform foo action.

    Attrs:
        bar: The value to perform the foo action on.
    """

    def __init__(self):
        """Construct."""
        self.bar = "bar"
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
- Check other other PEP257 conventions
