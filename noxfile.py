# type: ignore
import nox

nox.options.reuse_existing_virtualenvs = True

PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]
DEFAULT_PYTHON_VERSION = "3.8"


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test script."""
    # session.install("-r", "requirements-dev.txt")  # Install dev dependencies
    session.run("python", "-m", "unittest", "tests/tests.py")


@nox.session(python=DEFAULT_PYTHON_VERSION)
def lint(session: nox.Session) -> None:
    """Run the test script."""
    session.install("-r", "requirements-dev.txt")  # Install dev dependencies
    session.run("ruff", ".")
    session.run("ruff", "format", "--check", "-q", ".")
    session.run("mypy", "--install-types", "--non-interactive")
