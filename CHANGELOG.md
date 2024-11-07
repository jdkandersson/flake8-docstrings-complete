# Changelog

## [Unreleased]

## [v1.4.1] - 2024-11-07

### Added

- Support for Python 3.12 and 3.13 and Flake8 7.

## [v1.4.0] - 2024-11-07

### Added

- Exceptions for docstring contents for private functions.

## [v1.3.0] - 2023-11-29

### Added

- Support for `typing.overload`.

## [v1.2.0] - 2023-07-12

### Added

- Support for `functools.cached_property`.

## [v1.1.0] - 2023-01-26

### Added

- Lint check that ensures all function/ method arguments are described only
  once.
- Lint check that ensures all class attributes are described only once.
- Lint check that ensures all raised exceptions are described only once.

## [v1.0.4] - 2023-01-13

### Changed

- Changed only class attributes to be required in class attributes section,
  instance attributes are now optional

## [v1.0.3] - 2023-01-05

### Added

- Support for class properties

## [v1.0.2] - 2023-01-04

### Added

- Support for flake8 version 5

## [v1.0.1] - 2023-01-03

### Fixed

- Fixed definition of a section start to be a non-empty line rather than based
  on whether it has a named header

## [v1.0.0] - 2023-01-02

### Added

#### Function/ Method Arguments

- Lint check that ensures all function/ method arguments are documented
- Lint check that ensures docstring doesn't describe arguments the function/
  method doesn't have
- Lint check that ensures there is at most one arguments section in the
  docstring
- Lint check that ensures there is no empty arguments section in the docstring
- Support for unused arguments for which descriptions are optional
- Support `*args` and `**kwargs`
- Support positional only arguments
- Support keyword only arguments
- Support ignoring `self` and `cls` arguments
- Support for skipping test functions in test files
- Support for skipping test fixtures in test and fixture files
- Support async functions/ methods

#### Function/ Method Return Value

- Lint check that ensures all functions/ methods that return a value have the
  returns section in the docstring
- Lint check that ensures a function that does not return a value does not have
  the returns section
- Lint check that ensures there is at most one returns section in the docstring

#### Function/ Method Yield Value

- Lint check that ensures all functions/ methods that yield a value have the
  yields section in the docstring
- Lint check that ensures a function that does not yield a value does not have
  the yields section
- Lint check that ensures there is at most one yields section in the docstring

#### Function/ Method Exception Handling

- Lint check that ensures all function/ method exceptions are documented
- Lint check that ensures docstring doesn't describe exceptions the function/
  method doesn't raise
- Lint check that ensures there is at most one raises section in the docstring
- Lint check that ensures the raises section describes at least one exception

#### Class Attributes

- Lint check that ensures all class attributes are documented
- Lint check that ensures docstring doesn't describe attributes the class
  doesn't have
- Lint check that ensures there is at most one attributes section in the
  docstring
- Support for private attributes for which descriptions are optional
- Support for class attributes defined on the class and other `classmethod`
  methods
- Support for instance attributes defined in `__init__` and other non-static and
  non-`classmethod` methods
- Support async functions/ methods

[//]: # "Release links"
[v1.0.0]: https://github.com/jdkandersson/flake8-docstrings-complete/releases/v1.0.0
[v1.0.1]: https://github.com/jdkandersson/flake8-docstrings-complete/releases/v1.0.1
[v1.0.2]: https://github.com/jdkandersson/flake8-docstrings-complete/releases/v1.0.2
[v1.0.3]: https://github.com/jdkandersson/flake8-docstrings-complete/releases/v1.0.3
[v1.0.4]: https://github.com/jdkandersson/flake8-docstrings-complete/releases/v1.0.4
[v1.1.0]: https://github.com/jdkandersson/flake8-docstrings-complete/releases/v1.1.0
[v1.2.0]: https://github.com/jdkandersson/flake8-docstrings-complete/releases/v1.2.0
[v1.3.0]: https://github.com/jdkandersson/flake8-docstrings-complete/releases/v1.3.0
[v1.4.0]: https://github.com/jdkandersson/flake8-docstrings-complete/releases/v1.4.0
[v1.4.1]: https://github.com/jdkandersson/flake8-docstrings-complete/releases/v1.4.1
