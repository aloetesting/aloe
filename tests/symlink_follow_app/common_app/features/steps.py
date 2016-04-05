"""
Symlinked dummy feature step.
"""
# pylint:disable=unused-argument

from aloe import step


@step(r'I use symlinked step')
def step_symlinked(self):
    """Symlink step."""
    pass
