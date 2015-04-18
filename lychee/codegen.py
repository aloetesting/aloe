from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
# Code generation helpers

import ast
import re


FUNCTION_DEF_SAMPLE = ast.parse('def func(): pass')


def make_function(source, context=None, source_file=None, name=None):
    """
    Compile and evaluate given source to a function given the specified
    globals.
    Optionally set the file and name of the function.
    """

    func = ast.parse(source)

    # TODO: Check that generated code is a function
    if type(func) != type(FUNCTION_DEF_SAMPLE) \
            or len(func.body) != 1 \
            or type(func.body[0]) != type(FUNCTION_DEF_SAMPLE.body[0]):
        raise ValueError("source must be a function definition.")

    # Set or record the function name
    if name is not None:
        func.body[0].name = name
    else:
        name = func.body[0].name

    # TODO: What's a better default for file?
    if source_file is None:
        source_file = '<generated>'

    context = context or {}

    code = compile(func, source_file, 'exec')
    eval(code, context)

    return context[name]


def indent(source, count=1):
    """
    Indent the source by count*4 spaces.
    """

    prepend = ' ' * 4 * count
    return '\n'.join(
        # Only indent the non-empty lines
        prepend + line if line else line
        for line in source.split('\n')
    )


NOT_SPACE = re.compile('[^ ]')


def remove_indent(source):
    """
    Remove as much indentation as possible from the code.
    """

    lines = source.split('\n')
    min_indent = min(
        match.start() for match in (
            NOT_SPACE.search(line)
            for line in lines
        ) if match
    )

    return '\n'.join(
        line[min_indent:]
        for line in lines
    )
