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
import os
import re
import sys
import threading
import traceback

from lettuce.exceptions import StepLoadingError

world = threading.local()
world._set = False

real_stdout = sys.stdout


def _function_id(func):
    return (func.func_code.co_filename, func.func_code.co_firstlineno)


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
        step = self._assert_is_step(step, func)
        self[step] = func
        return func

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
        except re.error, e:
            raise StepLoadingError("Error when trying to compile:\n"
                                   "  regex: %r\n"
                                   "  for function: %s\n"
                                   "  error: %s" % (step, func, e))

    def _attr_is_step(self, attr, obj):
        return attr[0] != '_' and self._is_func_or_method(getattr(obj, attr))

    def _is_func_or_method(self, func):
        func_dir = dir(func)
        return callable(func) and ("func_name" in func_dir or "__func__" in func_dir)


STEP_REGISTRY = StepDict()
CALLBACK_REGISTRY = CallbackDict(
    {
        'all': {
            'before': {},
            'after': {},
        },
        'step': {
            'before_each': {},
            'after_each': {},
            'before_output': {},
            'after_output': {},
        },
        'scenario': {
            'before_each': {},
            'after_each': {},
            'outline': {},  # an example
        },
        'background': {
            'before_each': {},
            'after_each': {},
        },
        'feature': {
            'before_each': {},
            'after_each': {},
        },
        'scenario_outline': {
            'before_each': {},
            'after_each': {},
        },
        'example': {
            'before_each': {},
            'after_each': {},
        },
        'app': {
            'before_each': {},
            'after_each': {},
        },
        'harvest': {
            'before': {},
            'after': {},
        },
        'handle_request': {
            'before': {},
            'after': {},
        },
        'runserver': {
            'before': {},
            'after': {},
        },
    },
)


def call_hook(situation, kind, *args, **kw):
    for callback in CALLBACK_REGISTRY[kind][situation].values():
        try:
            callback(*args, **kw)
        except Exception as e:
            print >> real_stdout, "Exception in hook %s:" % callback.__name__
            traceback.print_exc(e, file=real_stdout)
            raise


def clear():
    STEP_REGISTRY.clear()
    CALLBACK_REGISTRY.clear()
