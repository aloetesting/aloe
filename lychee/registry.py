# -*- coding: utf-8 -*-
# Lychee - Cucumber runner for Python based on Lettuce and Nose
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import bytes
from builtins import super
from builtins import str
from future import standard_library
standard_library.install_aliases()

import re
from functools import wraps, partial

from lychee.exceptions import (
    NoDefinitionFound,
    StepLoadingError,
)


# What part of the test to hook
HOOK_WHAT = (
    'all',
    'feature',
    'example',
    'background',
    'scenario',
    'step',
)


# When to execute the hook in relation to the test part
HOOK_WHEN = (
    'before',
    'after',
    'around',
)


class CallbackDict(dict):
    def __init__(self):
        """
        Initialize the callback lists for every kind of situation.
        """
        super().__init__({
            what: {
                when: {}
                for when in HOOK_WHEN
            }
            for what in HOOK_WHAT
        })

    @staticmethod
    def _function_id(func):
        """
        A unique identifier of a function to prevent adding the same hook
        twice.

        To support dynamically generated functions, take the variables from
        the function closure into account.
        """
        return (
            func.__code__.co_filename,
            func.__code__.co_firstlineno,
            tuple(c.cell_contents for c in func.__closure__ or ()),
        )

    def append_to(self, what, when, function, name=None):
        """
        Add a callback for a particular type of hook.
        """
        # TODO: support priority for hook ordering
        if name is None:
            name = self._function_id(function)
        self[what][when].setdefault(name, function)

    def clear(self, name=None):
        """
        Remove all callbacks.
        """
        for action_dict in self.values():
            for callback_list in action_dict.values():
                if name is None:
                    callback_list.clear()
                else:
                    callback_list.pop(name, None)

    def wrap(self, what, function):
        """
        Return a function that executes all the callbacks in proper relations
        to the given test part.
        """

        # TODO: Code generation (not trivial as need to preserve the line
        # numbers later)?

        before = self[what]['before'].values()
        around = self[what]['around'].values()
        after = self[what]['after'].values()

        # Cannot loop 'with' statements without code generation
        for with_hook in around:
            @wraps(function)
            def wrap_with(*args, **kwargs):
                with with_hook():  # TODO: arguments
                    return function(*args, **kwargs)

            function = wrap_with

        @wraps(function)
        def wrapped(*args, **kwargs):
            for before_hook in before:
                before_hook()  # TODO: arguments

            # TODO: do 'after' hooks run after an exception?
            try:
                return function(*args, **kwargs)
            finally:
                for after_hook in after:
                    after_hook()  # TODO: arguments

        return wrapped


class StepDict(dict):
    def load(self, step, func):

        step = self._assert_is_step(step, func)
        self[step] = func

        try:
            func.sentence = step
            func.unregister = partial(self.unload, step)
        except AttributeError:
            # func might have been a bound method, no way to set attributes
            # on that
            pass

        return func

    def unload(self, step):
        try:
            del self[step]
        except KeyError:
            pass

    def load_func(self, func):
        regex = self._extract_sentence(func)
        return self.load(regex, func)

    def load_steps(self, obj):
        exclude = getattr(obj, "exclude", [])
        for attr in dir(obj):
            if self._attr_is_step(attr, obj) and attr not in exclude:
                step_method = getattr(obj, attr)
                self.load_func(step_method)
        return obj

    def _extract_sentence(self, func):
        func = getattr(func, '__func__', func)
        sentence = getattr(func, '__doc__', None)
        if sentence is None:
            sentence = func.__name__.replace('_', ' ')
            sentence = sentence[0].upper() + sentence[1:]
        return sentence

    def _assert_is_step(self, step, func):
        try:
            return re.compile(step, re.I | re.U)
        except re.error as e:
            raise StepLoadingError("Error when trying to compile:\n"
                                   "  regex: %r\n"
                                   "  for function: %s\n"
                                   "  error: %s" % (step, func, e))

    def _attr_is_step(self, attr, obj):
        return attr[0] != '_' and self._is_func_or_method(getattr(obj, attr))

    def _is_func_or_method(self, func):
        func_dir = dir(func)
        return callable(func) and (
            "func_name" in func_dir or
            "__func__" in func_dir)

    def match_step(self, step):
        """
        Find a function and arguments to call for a specified step.

        Returns a tuple of (function, args, kwargs).
        """

        for regex, func in self.items():
            matched = regex.search(step.sentence)
            if matched:
                kwargs = matched.groupdict()
                if kwargs:
                    return (func, (), matched.groupdict())
                else:
                    args = matched.groups()
                    return (func, args, {})

        raise NoDefinitionFound(step)


STEP_REGISTRY = StepDict()


def step(step_func_or_sentence):
    """Decorates a function, so that it will become a new step
    definition.
    You give step sentence either (by priority):
    * with step function argument (first example)
    * with function doc (second example)
    * with the function name exploded by underscores (third example)
    """
    if isinstance(step_func_or_sentence, bytes):
        # Python 2 strings, convert to str
        step_func_or_sentence = step_func_or_sentence.decode()

    if isinstance(step_func_or_sentence, str):
        return lambda func: STEP_REGISTRY.load(step_func_or_sentence, func)
    else:
        return STEP_REGISTRY.load_func(step_func_or_sentence)


CALLBACK_REGISTRY = CallbackDict()


class CallbackDecorator(object):
    """
    Add functions to the appropriate callback lists.
    """

    def __init__(self, when):
        self.when = when

    def _decorate(self, what, function, name=None):
        """
        Add the specified function (with name if given) to the callback list.
        """

        CALLBACK_REGISTRY.append_to(what, self.when, function, name=name)
        return function

    def make_decorator(what):
        """
        Make a decorator for a specific situation.
        """

        def decorator(self, function, name=None):
            return self._decorate(what, function, name=name)
        return decorator

    each_step = make_decorator('step')
    each_example = make_decorator('example')
    # TODO: More situations


after = CallbackDecorator('after')
around = CallbackDecorator('around')
before = CallbackDecorator('before')


def clear():
    STEP_REGISTRY.clear()
    CALLBACK_REGISTRY.clear()


def preserve_registry(func):
    """
    Create a registry context that will be unwrapped afterwards
    """

    @wraps(func)
    def inner(*args, **kwargs):
        step_registry = STEP_REGISTRY.copy()
        call_registry = CALLBACK_REGISTRY.copy()

        ret = func(*args, **kwargs)

        STEP_REGISTRY.clear()
        STEP_REGISTRY.update(step_registry)

        CALLBACK_REGISTRY.clear()
        CALLBACK_REGISTRY.update(call_registry)

        return ret

    return inner
