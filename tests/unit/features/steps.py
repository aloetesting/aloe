"""
Steps for features used in unit tests.
"""

from aloe import step


@step(r'I do nothing')
def trivial_step(self):  # pylint:disable=unused-argument
    """Trivial passing step."""
    pass


@step(r'I fail')
def failing_step(self):  # pylint:disable=unused-argument
    """Trivial failing step."""
    raise AssertionError("This step is meant to fail.")
