# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
# Copyright (C) <2014>  Danielle Madeley <danielle@madeley.id.au>
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
import unicodedata

from random import shuffle

from lettuce import parser, strings, languages
from lettuce.fs import FileSystem
from lettuce.registry import STEP_REGISTRY, call_hook
from lettuce.exceptions import (ReasonToFail,
                                FailFast,
                                NoDefinitionFound)

fs = FileSystem()


class StepDefinition(object):
    """
    A step definition is a wrapper for user-defined callbacks. It
    gets a few metadata from file, such as filename and line number
    """

    def __init__(self, step, function):
        self.function = function
        self.file = fs.relpath(function.func_code.co_filename)
        self.line = function.func_code.co_firstlineno + 1
        self.step = step

    def __call__(self, *args, **kw):
        """
        Method that actually wrapps the call to step definition
        callback. Sends step object as first argument
        """
        try:
            ret = self.function(self.step, *args, **kw)
            self.step.passed = True
        except (AssertionError, NoDefinitionFound) as e:
            self.step.failed = True
            self.step.why = ReasonToFail(self.step, e)
            raise e

        return ret

    def __unicode__(self):
        return '{file}:{line}'.format(file=self.file,
                                      line=self.line)

    def __repr__(self):
        return '<StepDefinition: {func} {file}:{line}>'.format(
            func=self.function.__name__,
            file=self.file,
            line=self.line)


class Step(parser.Step):
    """
    Object that represents each step on feature files.
    """

    has_definition = False
    defined_at = None
    why = None
    ran = False
    passed = None
    failed = None
    related_outline = None
    scenario = None

    @property
    def parent(self):
        return self.scenario or self.background

    def _get_match(self, ignore_case=True):
        matched, func = None, lambda: None

        for regex, func in STEP_REGISTRY.items():
            matched = re.search(regex, self.sentence, ignore_case and re.I or 0)
            if matched:
                break

        return matched, StepDefinition(self, func)

    def represented(self, indent=4, annotate=True):
        """
        Override the version of represented provided by the parser node
        to add the additional capability of annotating with the step
        definition
        """

        s = super(Step, self).represented(
            indent=indent,
            # steps without definitions return their feature file
            annotate=annotate and not self.has_definition)

        # steps with definitions return their step definition
        if annotate and self.has_definition:
            s = s.ljust(self.feature.max_length + 1) + \
                u'# ' + unicode(self.defined_at)

        return s

    def represent_traceback(self, indent=4):
        return u'\n'.join(u' ' * indent + line
                          for line in self.why.traceback.splitlines())

    def pre_run(self, ignore_case=True, with_outline=None):
        matched, step_definition = self._get_match(ignore_case)
        self.related_outline = with_outline

        if not self.defined_at:
            if not matched:
                raise NoDefinitionFound(self)

            self.has_definition = True
            self.defined_at = step_definition

        return matched, step_definition

    def given(self, string):
        return self.behave_as("Given " + string)

    def when(self, string):
        return self.behave_as("When " + string)

    def then(self, string):
        return self.behave_as("Then " + string)

    def behave_as(self, string):
        """
        Parses and run a step given in string form.

        In your step definitions, you can use this to run one step from another.

        e.g.
            @step('something ordinary')
            def something(step):
                step.behave_as('Given something defined elsewhere')

            @step('something defined elsewhere')
            def elsewhere(step):
                # actual step behavior, maybe.

        This will raise the error of the first failing step (thus halting
        execution of the step) if a subordinate step fails.
        """

        steps = self.parse_steps_from_string(string)

        for step in steps:
            step.__class__ = self.__class__
            step.scenario = self.scenario
            step.run()

    def run(self, ignore_case=True):
        """Runs a step, trying to resolve it on available step
        definitions"""
        matched, step_definition = self.pre_run(ignore_case=ignore_case)
        self.ran = True
        kw = matched.groupdict()

        if kw:
            step_definition(**kw)
        else:
            groups = matched.groups()
            step_definition(*groups)

        return True


class Scenario(parser.Scenario):
    """
    Object that represents each scenario on feature files.
    """

    @property
    def background(self):
        """
        The background for this scenario
        """

        return self.feature.background

    # FIXME -- these don't handle the concept of outlines at all
    @property
    def ran(self):
        return all(step.ran for step in self.steps)

    @property
    def passed(self):
        return self.ran and all(step.passed for step in self.steps)

    @property
    def failed(self):
        return any(step.failed for step in self.steps)

    def run(self, ignore_case=True, failfast=False):
        """
        Runs a scenario, running each of its steps. Also call
        before_each and after_each callbacks for steps and scenario

        The return value is not the results, but whether or not to keep
        running the tests. The results can be found at self.resultes
        """

        self.results = []

        if self.outlines:
            call_hook('before_each', 'scenario_outline', self)
            generator = self.evaluated
        else:
            generator = ((None, self.steps),)

        try:
            # before/after scenario hooks apply to the whole scenario or
            # scenario outline
            call_hook('before_each', 'scenario', self)

            for outline, steps in generator:
                try:
                    # before/after examples applies to a single example
                    call_hook('before_each', 'example', self, outline)

                    if self.background:
                        try:
                            self.background.run(ignore_case=ignore_case)

                        except (NoDefinitionFound, AssertionError) as e:
                            if failfast:
                                raise FailFast()

                            # fixtures failed, no point proceeding
                            continue

                    # pre-run the steps so we have their definitions set
                    for step in steps:
                        try:
                            step.pre_run(ignore_case=ignore_case,
                                         with_outline=outline)
                        except NoDefinitionFound:
                            pass

                    # run the steps for real
                    failed = False
                    for step in steps:
                        try:
                            call_hook('before_each', 'step', step)
                            call_hook('before_output', 'step', step)

                            if not failed:
                                step.run(ignore_case=ignore_case)

                        except Exception as e:
                            # we expect steps to assert or not be found
                            if failfast:
                                raise FailFast()

                            # we still need to emit signals for the skipped
                            # steps, else they won't be rendered by the
                            # output plugin
                            failed = True

                        finally:
                            call_hook('after_output', 'step', step)
                            call_hook('after_each', 'step', step)

                except FailFast:
                    raise

                finally:
                    if outline:
                        call_hook('outline', 'scenario', self,
                                  None, outline, None)
                        call_hook('after_each', 'example', self, outline)

                    steps_passed = [step for step in steps if step.passed]
                    steps_failed = [step for step in steps if step.failed]
                    steps_undefined = [step for step in steps
                                       if not step.has_definition]
                    steps_skipped = [step for step in steps
                                     if step.has_definition and not step.ran]

                    self.results.append(ScenarioResult(self,
                                                       steps_passed,
                                                       steps_failed,
                                                       steps_skipped,
                                                       steps_undefined))

            if self.outlines:
                call_hook('after_each', 'scenario_outline', self)

        finally:
            call_hook('after_each', 'scenario', self)

        return self.results


class Background(parser.Background):

    def run(self, ignore_case=True):
        try:
            call_hook('before_each', 'background', self)

            for step in self.steps:
                try:
                    call_hook('before_each', 'step', step)
                    call_hook('before_output', 'step', step)

                    # any exception generated here will be caught in
                    # Scenario.run()
                    step.run(ignore_case=ignore_case)

                finally:
                    call_hook('after_output', 'step', step)
                    call_hook('after_each', 'step', step)

        finally:
            call_hook('after_each', 'background', self, results)

    def __repr__(self):
        return '<Background for feature: {0}>'.format(self.feature.name)


class Feature(parser.Feature):
    """
    Object that represents a feature.
    """

    @classmethod
    def _hack_class(cls, self):
        """
        Hackily cast the classes from the parser class to the core class
        """

        self.__class__ = cls

        if self.background:
            self.background.__class__ = Background

        for scenario in self.scenarios:
            scenario.__class__ = Scenario

            for step in scenario.steps:
                step.__class__ = Step

        return self

    @classmethod
    def from_string(cls, *args, **kwargs):
        """
        Parse a feature from a string
        """

        self = parser.Feature.from_string(*args, **kwargs)
        self = cls._hack_class(self)

        return self

    @classmethod
    def from_file(cls, *args, **kwargs):
        """
        Parse a feature from a file
        """

        self = parser.Feature.from_file(*args, **kwargs)
        self = cls._hack_class(self)

        return self

    def run(self, scenarios=None,
            ignore_case=True,
            tags=None,
            random=False,
            failfast=False):

        tags = tags or []

        if scenarios:
            scenarios = [self.scenarios[i-1] for i in scenarios
                         if isinstance(i, int)]
        else:
            scenarios = self.scenarios

        scenarios = [scenario for scenario in scenarios
                     if scenario.matches_tags(tags)]

        # If no scenarios in this feature will run,
        # but don't run the feature hooks.
        if not scenarios:
            return FeatureResult(self)

        if random:
            shuffle(scenarios)

        results = []

        try:
            call_hook('before_each', 'feature', self)

            for scenario in scenarios:
                try:
                    scenario.run(ignore_case=ignore_case,
                                 failfast=failfast)

                except FailFast:
                    break

                finally:
                    results += scenario.results

        finally:
            call_hook('after_each', 'feature', self)

        return FeatureResult(self, *results)


class FeatureResult(object):
    """Object that holds results of each scenario ran from within a feature"""
    def __init__(self, feature, *scenario_results):
        self.feature = feature
        self.scenario_results = scenario_results

    @property
    def passed(self):
        return all([result.passed for result in self.scenario_results])


class ScenarioResult(object):
    """Object that holds results of each step ran from within a scenario"""
    def __init__(self, scenario, steps_passed, steps_failed, steps_skipped,
                 steps_undefined):

        self.scenario = scenario

        self.steps_passed = steps_passed
        self.steps_failed = steps_failed
        self.steps_skipped = steps_skipped
        self.steps_undefined = steps_undefined

        all_lists = [steps_passed + steps_skipped + steps_undefined + steps_failed]
        self.total_steps = sum(map(len, all_lists))

    @property
    def passed(self):
        return self.total_steps is len(self.steps_passed)


class TotalResult(object):
    def __init__(self, feature_results):
        self.feature_results = feature_results
        self.scenario_results = []
        self.steps_passed = 0
        self.steps_failed = 0
        self.steps_skipped = 0
        self.steps_undefined = 0
        self._proposed_definitions = []
        self.steps = 0
        # store the scenario names that failed, with their location
        self.failed_scenario_locations = []
        for feature_result in self.feature_results:
            for scenario_result in feature_result.scenario_results:
                self.scenario_results.append(scenario_result)
                self.steps_passed += len(scenario_result.steps_passed)
                self.steps_failed += len(scenario_result.steps_failed)
                self.steps_skipped += len(scenario_result.steps_skipped)
                self.steps_undefined += len(scenario_result.steps_undefined)
                self.steps += scenario_result.total_steps
                self._proposed_definitions.extend(scenario_result.steps_undefined)
                if len(scenario_result.steps_failed) > 0:
                    self.failed_scenario_locations.append(scenario_result.scenario.represented())

    def _filter_proposed_definitions(self):
        return []
        # sentences = []
        # for step in self._proposed_definitions:
        #     if step.proposed_sentence not in sentences:
        #         sentences.append(step.proposed_sentence)
        #         yield step

    @property
    def proposed_definitions(self):
        return list(self._filter_proposed_definitions())

    @property
    def features_ran(self):
        return len(self.feature_results)

    @property
    def features_passed(self):
        return len([result for result in self.feature_results if result.passed])

    @property
    def scenarios_ran(self):
        return len(self.scenario_results)

    @property
    def scenarios_passed(self):
        return len([result for result in self.scenario_results if result.passed])
