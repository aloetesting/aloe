"""
Useful tools for writing Aloe steps.

See also :class:`aloe.world`.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import

import re
import inspect
from datetime import datetime
from functools import wraps


def guess_types(data):  # pylint:disable=too-complex
    """
    Converts a record or list of records from strings contained in
    outlines, table or hashes into a version with the types guessed.

    :param data: a :attr:`Scenario.outlines`, :attr:`Step.table`,
        :attr:`Step.hashes` or any other :class:`list`,
        list of lists or list of dicts.

    Will guess the following (in priority order):

     * :class:`bool` (``true``/``false``)
     * :class:`None` (``null``)
     * :class:`int`
     * :class:`date` in ISO format (``yyyy-mm-dd``)
     * :class:`str`

    The function operates recursively, so you should be able to pass nearly
    anything to it. At the very least basic types plus
    :class:`dict` and iterables.
    """

    # convert bytes to strings
    if isinstance(data, bytes):
        data = data.decode()

    if isinstance(data, str):
        # pylint:disable=redefined-variable-type
        if data == "true":
            data = True
        elif data == "false":
            data = False
        elif data == "null":
            data = None
        elif data.isdigit() and not re.match("^0[0-9]+", data):
            data = int(data)
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', data):
            data = datetime.strptime(data, "%Y-%m-%d").date()
        else:
            # it's a string
            pass

        return data
        # pylint:enable=redefined-variable-type

    # if it's a dict, recurse as a dict
    if isinstance(data, dict):
        return {
            guess_types(key): guess_types(data)
            for key, data in data.items()
        }

    # try to recurse as an iterable
    try:
        return [guess_types(val) for val in data]
    except TypeError:
        pass

    #  give up
    return data


def hook_not_reentrant(func):
    """
    Decorate a hook as unable to be reentered while it is already in the
    stack.

    Any further attempts to enter the hook before exiting will be replaced
    by a no-op.

    This is generally useful for step hooks where a step might call
    :meth:`Step.behave_as` and trigger a second level of step hooks i.e.
    when displaying information about the running test.
    """

    # closure-scoped variable to track whether this hook has been
    # entered
    entered = [False]

    @wraps(func)
    def inner(*args, **kwargs):
        """
        Wrap func to check if we've already entered this function and if
        so replace it with a no-op.
        """

        def generator():
            """
            Hide the generator in a separate function
            because Python 2 can't support "returning from generators"
            """
            if entered[0]:
                yield
            else:
                try:
                    entered[0] = True
                    for val in func(*args, **kwargs):
                        yield val
                finally:
                    entered[0] = False

        if inspect.isgeneratorfunction(func):
            return generator()
        else:
            if not entered[0]:
                try:
                    entered[0] = True
                    return func(*args, **kwargs)
                finally:
                    entered[0] = False

    return inner
