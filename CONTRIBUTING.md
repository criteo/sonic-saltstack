# Developer guide

## Requirements

**unit and functionals tests** are mandatory.

Please ensure you have run the following before pushing a commit:
  * `black` and `isort` (or `invoke reformat`)
  * `tox` to run all linters

## Coding style

Follow usual best practices:
  * document your code (inline and docstrings)
  * constant are in upper case
  * use comprehensible variable name
  * one function = one purpose
  * function name should define perfectly its purpose
