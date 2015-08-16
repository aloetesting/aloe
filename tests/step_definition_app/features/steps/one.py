"""
Part of steps for the tested application.
"""
# pylint:disable=unused-argument

from aloe import step


@step(r'I use step one')
def step_one(self):
    """Dummy step."""
    pass
