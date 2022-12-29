# flake8-docstring

Linter that checks docstrings of functions, methods and classes. It should be
used in conjuction with `pydocstyle` as the linter assumes that the docstrings
already pass `pydocstyle` checks. `flake8-docstring` adds the following checks
to complement `pydocstyle`:

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
10. There is only one section for each of the arguments, return value, yield
  value, raises and attributes.

Note:
* `self` and `cls` are not counted as arguments.
* `__init__` methods are skipped.
* `test_.*` methods are skipped in `test_.*\.py` files (function and file names
  are configurable).

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
        """Construct."""

        self.bar = bar
```

## Sections

There are several alternative names for each of the sections which are captured
case-insensitive:

* arguments: `Args`, `Arguments`, `Parameters`
* return value: `Return`, `Returns`
* yield value: `Yield`, `Yields`
* raise: `Raises`
* attributes: `Attrs`, `Attributes`

Section information is extracted using the following algorithm:

1. Look for a line that has zero or more whitespace characters, followed by a
  section name (non-case-sensistive) followed by a colon.
2. Look for any sub-sections on a line which starts with zero or more
  whitespace characters followed by a word, optionally followed by whitespace
  and any characters within round brackets followed by a colon.
3. The section ends if any line with zero or more whitespace characters is
  encountered.
