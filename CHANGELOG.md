# Changelog

## [Unreleased]

## [v1.0.0] - 2023-01-02

### Added

#### Function/ Method Arguments

- Lint check that ensures all function/ method arguments are documented
- Lint check that ensures docstring doesn't describe arguments the function/
  method doesn't have
- Lint check that ensures there is only one args section in the docstring
- Support `*args` and `**kwargs`
- Support positional only arguments
- Support keyword only arguments
- Support ignoring `self` and `cls` arguments
- Support for skipping test functions in test files
- Support for skipping test fixtures in test and fixture files
- Support async functions

#### Function/ Method Return Value

- Lint check that ensures all functions/ methods that return a value have the
  returns section in the docstring
- Lint check that ensures a function that does not return a value does not have
  the returns section
- Lint check that ensures there is only one returns section in the docstring

#### Function/ Method Yield Value

- Lint check that ensures all functions/ methods that yield a value have the
  yields section in the docstring
- Lint check that ensures a function that does not yield a value does not have
  the yields section
- Lint check that ensures there is only one yields section in the docstring

#### Function/ Method Exception Handling

- Lint check that ensures all function/ method exceptions are documented
- Lint check that ensures docstring doesn't describe exceptions the function/
  method doesn't raise
- Lint check that ensures there is only one raises section in the docstring
- Lint check that ensures the raises section describes at least one exception.

[//]: # "Release links"
[v1.0.0]: https://github.com/jdkandersson/flake8-docstrings-complete/releases/v1.0.0
