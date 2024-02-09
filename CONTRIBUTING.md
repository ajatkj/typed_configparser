# Contributing

I'd love you to contribute to typed_configparser!

## Issues

Questions, feature requests and bug reports are all welcome as [discussions or issues](https://github.com/ajatkj/typed_configparser/issues/new/choose).

To make it as simple as possible for us to help you, please include the output of the following call in your issue:

```bash
python -c "import typed_configparser; print(typed_configparser.__version__)"
```

## Pull Requests

It should be extremely simple to get started and create a Pull Request.

Unless your change is trivial (typo, etc.), please create an issue to discuss the change before creating a pull request.

To make contributing as easy and fast as possible, you'll want to run tests and linting locally.

## Prerequisites

You'll need the following prerequisites:

Any Python version between Python 3.8 and 3.12

- a virtual environment tool
- git
- pyenv & nox (to optionally test your changes on all versions of python)

## Installation and setup

Fork the repository on GitHub and clone your fork locally.

```sh
# Clone your fork and cd into the repo directory
git clone git@github.com:<your username>/typed_configparser.git
cd typed_configparser
```

## Install typed-configparser locally

```sh
# Create the virtual environment using your favourite tool
python3 -m venv env

# Activate the virtual environment
source env/bin/activate

# Install typed-configparser in your virtual environment
# This will install all development dependencies to help you get start
python3 -m pip install -r requirements.txt
```

## Check out a new branch and make your changes

Create a new branch for your changes.

```sh
# Checkout a new branch and make your changes
git checkout -b my-new-feature-branch
# Make your changes...
```

## Run tests and linting

Run tests and linting locally to make sure everything is working as expected.

```sh
# Run automated code formatting and linting
poe lint
# typed_configparser uses ruff for linting and formatting
# https://github.com/astral-sh/ruff

# Run tests and linting
poe test
# There are few commands set-up using poethepoet task manager.
# You can check list of all commands using `poe`
# https://github.com/nat-n/poethepoet

# Check test coverage
# Make sure test coverage is 100% else PR will fail in CI pipeline.
poe coverage
poe converage_report
```

## Run automation test on all python versions

You can optionally run tests and linting on all python versions from 3.8 to 3.12 to make sure code is compliant across all supported python versions.
If you don't do this, any errors will be caught in the PR check phase.

```sh
# Install pyenv using https://github.com/pyenv/pyenv?tab=readme-ov-file#installation
# Install nox using https://nox.thea.codes/en/stable/
# You can either install it globally or using pipx (do not install it in project virtual environment)

# Install all supported python versions using pyenv
pyenv install 3.8 && pyenv install 3.9 && pyenv install 3.10 && pyenv install 3.11 && pyenv install 3.12

# Go to project root and set pyenv global environment (do not activate project virtual environment)
pyenv global 3.8 3.9 3.10 3.11 3.12

# Run nox
nox
```

## Commit and push your changes

Commit your changes, push your branch to GitHub, and create a pull request.

Please follow the pull request template and fill in as much information as possible. Link to any relevant issues and include a description of your changes.

When your pull request is ready for review, add a comment with the message "please review" and we'll take a look as soon as we can.
