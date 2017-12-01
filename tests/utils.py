"""
Utilities for tests.
"""

import os
from contextlib import contextmanager


def appender(target, *args):
    """
    A function that appends given arguments and its own to the specified
    list.
    """

    def append(*append_args):
        """Append the earlier specified and given arguments to the target."""
        target.append(args + append_args)

    return append


def before_after(before, after):
    """
    A context manager calling given functions before and after the context,
    respectively, with the same arguments as it is given itself.
    """

    @contextmanager
    def around(*args, **kwargs):
        """Call given functions before and after the context."""
        before(*args, **kwargs)
        yield
        after(*args, **kwargs)

    return around


@contextmanager
def set_environ(**kwargs):
    """
    A context manager setting environment variable to given values before the
    context and restoring them afterwards.
    """

    old_values = {}
    for key, value in kwargs.items():
        old_values[key] = os.environ.get(key, None)
        os.environ[key] = value

    try:
        yield

    finally:
        for key, value in old_values.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value
