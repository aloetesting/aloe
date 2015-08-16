"""
Part of steps for the tested application.
"""

# pylint:disable=unused-argument,unused-import

from aloe import step

from .one import step_one


@step(r'I use step two')
def step_two(self):
    """Dummy step."""
    pass
