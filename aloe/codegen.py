"""
Code generation helpers
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

import ast
from contextlib import contextmanager
from textwrap import dedent

from aloe.utils import identifier


FUNCTION_DEF_SAMPLE = ast.parse('def func(): pass')


def make_function(source, context=None, source_file=None, name=None):
    """
    Compile and evaluate given source to a function given the specified
    globals.
    Optionally set the file and name of the function.
    """

    func = ast.parse(source)

    # Check that generated code is a function
    # pylint:disable=unidiomatic-typecheck
    if type(func) != type(FUNCTION_DEF_SAMPLE) \
            or len(func.body) != 1 \
            or type(func.body[0]) != type(FUNCTION_DEF_SAMPLE.body[0]):
        raise ValueError("source must be a function definition.")
    # pylint:enable=unidiomatic-typecheck

    # Set or record the function name
    if name is not None:
        func.body[0].name = name = identifier(name)
    else:
        name = func.body[0].name

    # TODO: What's a better default for file?
    if source_file is None:
        source_file = '<generated>'

    context = context or {}

    code = compile(func, source_file, 'exec')
    eval(code, context)  # pylint:disable=eval-used

    return context[name]


def multi_manager(*managers):
    """
    A context manager invoking all the given context managers in order.

    Returns a tuple with all the manager results.
    """

    if len(managers) == 0:
        source = dedent(
            """
            def null_manager(*args, **kwargs):
                yield ()
            """
        )
    else:
        with_stmt = ', '.join(
            "manager{i}(*args, **kwargs) as result{i}".format(i=i)
            for i in range(len(managers))
        )

        result_tuple = '(' + ', '.join(
            "result{i}".format(i=i)
            for i in range(len(managers))
        ) + ')'

        source = dedent(
            """
            def multi_manager(*args, **kwargs):
                with {with_stmt}:
                    yield {result_tuple}
            """
        ).format(with_stmt=with_stmt, result_tuple=result_tuple)

    context = {
        'manager' + str(i): manager
        for i, manager in enumerate(managers)
    }

    return contextmanager(make_function(
        source=source,
        context=context,
    ))
