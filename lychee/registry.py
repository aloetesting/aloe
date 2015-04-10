# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
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
import re
import threading
from functools import wraps, partial

from lychee.exceptions import (
    NoDefinitionFound,
    StepLoadingError,
)


def _function_id(func):
    return (
        func.func_code.co_filename,
        func.func_code.co_firstlineno,
        tuple(c.cell_contents for c in func.func_closure or ()),
    )


class CallbackDict(dict):
    def append_to(self, where, when, function, name=None):
        if name is None:
            name = _function_id(function)
        self[where][when].setdefault(name, function)

    def clear(self, name=None):
        for _, action_dict in self.items():
            for callback_list in action_dict.values():
                if name is None:
                    callback_list.clear()
                else:
                    callback_list.pop(name, None)

class StepDict(dict):
    def load(self, step, func):
        func.sentence = step

        step = self._assert_is_step(step, func)
        self[step] = func

        func.unregister = partial(self.unload, step)

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
            sentence = func.func_name.replace('_', ' ')
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


def clear():
    STEP_REGISTRY.clear()


def preserve_registry(func):
    """
    Create a registry context that will be unwrapped afterwards
    """

    @wraps(func)
    def inner(*args, **kwargs):
        step_registry = STEP_REGISTRY.copy()

        ret = func(*args, **kwargs)

        STEP_REGISTRY.clear()
        STEP_REGISTRY.update(step_registry)

        return ret

    return inner
