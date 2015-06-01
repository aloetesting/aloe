"""
Steps for testing running multiple apps together.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from aloe import (
    before,
    step,
    world,
)


@before.all
def start_one():
    world.app_one_started = True


@step(r'I record the started callbacks in app one')
def check_callbacks_one(self):
    world.started_callbacks_one = {
        'one': getattr(world, 'app_one_started', None),
        'two': getattr(world, 'app_two_started', None),
    }
