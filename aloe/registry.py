# -*- coding: utf-8 -*-
# Aloe - Cucumber runner for Python based on Lettuce and Nose
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
from collections import OrderedDict
from functools import wraps, partial

from aloe.codegen import multi_manager
from aloe.exceptions import (
    NoDefinitionFound,
    StepLoadingError,
)


# What part of the test to hook
HOOK_WHAT = (
    'all',
    'feature',
    'example',
    'step',
)


# When to execute the hook in relation to the test part
HOOK_WHEN = (
    'before',
    'after',
    'around',
)


class PriorityClass(object):
    """
    Priority class constants.
    """

    SYSTEM_OUTER = -10  # System callbacks executing before others
    USER = 0  # User callbacks
    SYSTEM_INNER = 10  # System callbacks executing after others

    # Note that for 'after' and the 'after' part of 'around' callbacks,
    # the order is reversed


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

    @classmethod
    def _function_id(cls, func):
        """
        A unique identifier of a function to prevent adding the same hook
        twice.

        To support dynamically generated functions, take the variables from
        the function closure into account.
        """

        if hasattr(func, '__wrapped__'):
            return cls._function_id(func.__wrapped__)

        return (
            func.__code__.co_filename,
            func.__code__.co_firstlineno,
            # variables in the closure might not be hashable
            tuple(str(c.cell_contents) for c in func.__closure__ or ()),
        )

    def append_to(self, what, when, function, name=None, priority=0):
        """
        Add a callback for a particular type of hook.
        """
        if name is None:
            name = self._function_id(function)

        funcs = self[what][when].setdefault(priority, OrderedDict())
        funcs.pop(name, None)
        funcs[name] = function

    def clear(self, name=None, priority_class=None):
        """
        Remove matching callbacks.
        If name is given, only remove callbacks with given name.
        If a priority class is given, only remove ones with the given class.
        """
        for what_dict in self.values():
            for when_dict in what_dict.values():
                if priority_class is None:
                    action_values = when_dict.values()
                else:
                    action_values = (
                        value
                        for (pc, _), value
                        in when_dict.items()
                        if pc == priority_class
                    )
                for callback_list in action_values:
                    if name is None:
                        callback_list.clear()
                    else:
                        callback_list.pop(name, None)

    def hook_list(self, what, when):
        """
        Get all the hooks for a certain event, sorted appropriately.
        """
        return tuple(
            func
            for priority in sorted(self[what][when].keys())
            for func in self[what][when][priority].values()
        )

    def wrap(self, what, function, *hook_args, **hook_kwargs):
        """
        Return a function that executes all the callbacks in proper relations
        to the given test part.
        """

        before = self.hook_list(what, 'before')
        around = self.hook_list(what, 'around')
        after = self.hook_list(what, 'after')

        multi_hook = multi_manager(*around)

        @wraps(function)
        def wrapped(*args, **kwargs):
            for before_hook in before:
                before_hook(*hook_args, **hook_kwargs)

            try:
                with multi_hook(*hook_args, **hook_kwargs):
                    return function(*args, **kwargs)
            finally:
                # 'after' hooks still run after an exception
                for after_hook in reversed(after):
                    after_hook(*hook_args, **hook_kwargs)

        return wrapped

    def before_after(self, what):
        """
        Return a pair of functions to execute before and after the event.
        """

        before = self.hook_list(what, 'before')
        around = self.hook_list(what, 'around')
        after = self.hook_list(what, 'after')

        multi_hook = multi_manager(*around)

        # Save in a closure for both functions
        around_hook = [None]

        def before_func(*args, **kwargs):
            for before_hook in before:
                before_hook(*args, **kwargs)

            around_hook[0] = multi_hook(*args, **kwargs)
            around_hook[0].__enter__()

        def after_func(*args, **kwargs):
            around_hook[0].__exit__(None, None, None)
            around_hook[0] = None

            for after_hook in after:
                after_hook(*args, **kwargs)

        return before_func, after_func


class StepDict(dict):
    def load(self, step, func):

        step_re = self._assert_is_step(step, func)
        self[step_re] = func

        try:
            func.sentence = step
            func.unregister = partial(self.unload, step_re)
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

    def step(self, step_func_or_sentence):
        """
        Decorates a function, so that it will become a new step
        definition.
        You give step sentence either (by priority):
        * with step function argument
        * with function doc
        * with the function name exploded by underscores
        """

        if isinstance(step_func_or_sentence, bytes):
            # Python 2 strings, convert to str
            step_func_or_sentence = step_func_or_sentence.decode()

        if isinstance(step_func_or_sentence, str):
            return lambda func: self.load(step_func_or_sentence, func)
        else:
            return self.load_func(step_func_or_sentence)


STEP_REGISTRY = StepDict()


step = STEP_REGISTRY.step


CALLBACK_REGISTRY = CallbackDict()


class CallbackDecorator(object):
    """
    Add functions to the appropriate callback lists.
    """

    def __init__(self, registry, when, priority_class=PriorityClass.USER):
        self.registry = registry
        self.when = when
        self.priority_class = priority_class

    def _decorate(self, what, function, name=None, priority=0):
        """
        Add the specified function (with name if given) to the callback list.
        """

        priority = (self.priority_class, priority)

        self.registry.append_to(what, self.when, function,
                                name=name,
                                priority=priority)
        return function

    def make_decorator(what):
        """
        Make a decorator for a specific situation.
        """

        def decorator(self, function, **kwargs):
            return self._decorate(what, function, **kwargs)
        return decorator

    each_step = make_decorator('step')
    each_example = make_decorator('example')
    each_feature = make_decorator('feature')
    all = make_decorator('all')


after = CallbackDecorator(CALLBACK_REGISTRY, 'after')
around = CallbackDecorator(CALLBACK_REGISTRY, 'around')
before = CallbackDecorator(CALLBACK_REGISTRY, 'before')
