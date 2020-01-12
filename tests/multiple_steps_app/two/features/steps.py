"""
Steps for testing running multiple apps together.
"""

from aloe import (
    before,
    step,
    world,
)


@before.all
def start_two():
    """Mark the app two as started."""
    world.app_two_started = True


@step(r'I record the started callbacks in app two')
def check_callbacks_two(self):
    """Check which apps were started."""
    world.started_callbacks_two = {
        'one': getattr(world, 'app_one_started', None),
        'two': getattr(world, 'app_two_started', None),
    }
