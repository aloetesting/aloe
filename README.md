Aloe
====

[![Build status](https://img.shields.io/travis/aloetesting/aloe.svg)](https://travis-ci.org/aloetesting/aloe)
[![Coverage](https://img.shields.io/coveralls/aloetesting/aloe.svg)](https://coveralls.io/github/aloetesting/aloe)
[![PyPI](https://img.shields.io/pypi/v/aloe.svg)](https://pypi.python.org/pypi/aloe)

A [Gherkin][gherkin] runner for Python based on [Nose][nose] and
[Lettuce][lettuce].

Install:

    pip install aloe

Read the [documentation][docs].

Invocation
----------

`aloe` command line tool is a wrapper for the `nose` runner, configured to only
run Gherkin tests. As such, the invocation is the same as `nose`, but the
following parameters are added:

* `-n N[,N...]` - only run the specified scenarios (by number, 1-based) in each
  feature. Makes sense when only specifying one feature to run, for example

  `aloe features/calculator.feature -n 1`

* `--test-class` - override the class used as a base for each feature.

* `--no-ignore-python` - run Python tests as well as Gherkin.

Migrating from Lettuce
----------------------

Aloe, started as a fork of Lettuce, tries to be compatible where it makes
sense. However, there are following incompatible changes:

* `each_scenario` and `each_background` callbacks are removed. Use
  `each_example`.
* `-s` option for running particular scenarios is renamed to `-n`.
* Django-related functionality, including the `harvest` command, is moved to a
  separate project, [Aloe-Django][aloe-django].
* `terrain.py` has no particular significance. It will be imported but only if
  it exists at the same directory with the other step definition files, and not
  above it.
* Scenario outlines must be declared with "Scenario Outline", and scenarios
  without examples must use "Scenario" - Lettuce allowed using either.
* By default, the steps run are output as dots, corresponding to Lettuce
  verbosity 1. To get colored output with steps printed as they run, use `-v 3`.

License
-------

Aloe - Cucumber runner for Python based on Lettuce and Nose

Copyright (C) <2015> Alexey Kotlyarov <a@koterpillar.com>

Copyright (C) <2014-2015> Danielle Madeley <danielle@madeley.id.au>

Copyright (C) <2010-2012> Gabriel Falcão <gabriel@nacaolivre.org>


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

[gherkin]: https://cucumber.io/
[nose]: https://nose.readthedocs.io/
[nose-plugin-attrib]: https://nose.readthedocs.io/en/latest/plugins/attrib.html
[lettuce]: http://lettuce.it/
[gherkin-syntax]: https://cucumber.io/docs/reference
[aloe-django]: https://github.com/aloetesting/aloe_django
[docs]: http://aloe.readthedocs.io/
