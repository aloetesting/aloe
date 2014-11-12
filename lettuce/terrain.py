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
from functools import wraps

from lettuce.registry import world
from lettuce.registry import CALLBACK_REGISTRY


world._set = True


def absorb(thing, name=None):
    if not isinstance(name, basestring):
        name = thing.__name__

    setattr(world, name, thing)
    return thing

world.absorb = absorb


@world.absorb
def spew(name):
    if hasattr(world, name):
        item = getattr(world, name)
        delattr(world, name)
        return item


def callback(where, when):
    """
    This is a bit tricky.

    @callback is a decorator factory, i.e. a decorator that creates
    decorators. It takes two properties, `where' and `when' which are
    used to register the callback with the registry as well as the method
    we are turning into a decorator.

    The inner method registers the func with the callback registry.
    """

    def outer(method):

        method.__callback__ = {}

        @wraps(method)
        def inner(self, callback, name=None):
            if not callable(callback):
                name = callback
                return lambda callback: inner(self, callback, name=name)

            CALLBACK_REGISTRY.append_to(
                where,
                when.format(name=self.name),
                function=callback,
                name=name,
            )

            return callback

        return inner

    return outer


class Main(object):

    def __init__(self, name):
        self.name = name

    @callback('all', '{name}')
    def all(fn):
        pass

    @callback('step', '{name}_each')
    def each_step(fn):
        pass

    @callback('step', '{name}_output')
    def step_output(fn):
        pass

    @callback('scenario', '{name}_each')
    def each_scenario(fn):
        pass

    @callback('example', '{name}_each')
    def each_example(fn):
        pass

    @callback('background', '{name}_each')
    def each_background(fn):
        pass

    @callback('feature', '{name}_each')
    def each_feature(fn):
        pass

    @callback('harvest', '{name}')
    def harvest(fn):
        pass

    @callback('app', '{name}_each')
    def each_app(*args):
        pass

    @callback('runserver', '{name}')
    def runserver(*args):
        pass

    @callback('handle_request', '{name}')
    def handle_request(*args):
        pass

    @callback('scenario', 'outline')
    def outline():
        pass


before = Main('before')
after = Main('after')
