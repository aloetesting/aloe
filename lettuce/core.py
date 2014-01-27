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
import codecs
import unicodedata

from copy import deepcopy
from itertools import chain
from random import shuffle

from lettuce import parser, strings, languages
from lettuce.fs import FileSystem
from lettuce.registry import STEP_REGISTRY, call_hook
from lettuce.exceptions import (ReasonToFail,
                                FailFast,
                                NoDefinitionFound,
                                LettuceSyntaxError)

fs = FileSystem()


# class REP(object):
#     "RegEx Pattern"
#     first_of = re.compile(ur'^first_of_')
#     last_of = re.compile(ur'^last_of_')
#     language = re.compile(u"language:[ ]*([^\s]+)")
#     within_double_quotes = re.compile(r'("[^"]+")')
#     within_single_quotes = re.compile(r"('[^']+')")
#     only_whitespace = re.compile('^\s*$')
#     last_tag_extraction_regex = re.compile(ur'(?:\s|^)[@](\S+)\s*$')
#     first_tag_extraction_regex = re.compile(ur'^\s*[@](\S+)(?:\s|$)')
#     tag_strip_regex = re.compile(ur'(?:(?:^\s*|\s+)[@]\S+\s*)+$', re.DOTALL)
#     comment_strip1 = re.compile(ur'(^[^\'"]*)[#]([^\'"]*)$')
#     comment_strip2 = re.compile(ur'(^[^\'"]+)[#](.*)$')


# class HashList(list):
#     __base_msg = 'The step "%s" have no table defined, so ' \
#         'that you can\'t use step.hashes.%s'
#
#     def __init__(self, step, *args, **kw):
#         self.step = step
#         super(HashList, self).__init__(*args, **kw)
#
#     def values_under(self, key):
#         msg = 'The step "%s" have no table column with the key "%s". ' \
#             'Could you check your step definition for that ? ' \
#             'Maybe there is a typo :)'
#
#         try:
#             return [h[key] for h in self]
#         except KeyError:
#             raise AssertionError(msg % (self.step.sentence, key))
#
#     @property
#     def first(self):
#         if len(self) > 0:
#             return self[0]
#
#         raise AssertionError(self.__base_msg % (self.step.sentence, 'first'))
#
#     @property
#     def last(self):
#         if len(self) > 0:
#             return self[-1]
#
#         raise AssertionError(self.__base_msg % (self.step.sentence, 'last'))


class Language(object):
    code = 'en'
    name = 'English'
    native = 'English'
    feature = 'Feature'
    scenario = 'Scenario'
    examples = 'Examples|Scenarios'
    scenario_outline = 'Scenario Outline'
    scenario_separator = 'Scenario( Outline)?'
    background = "Background"

    def __init__(self, code=u'en'):
        self.code = code
        for attr, value in languages.LANGUAGES[code].items():
            setattr(self, attr, unicode(value))

    def __repr__(self):
        return '<Language "%s">' % self.code

    def __getattr__(self, attr):
        # for pattern in [REP.first_of, REP.last_of]:
        #     if pattern.match(attr):
        #         name = pattern.sub(u'', attr)
        #         return unicode(getattr(self, name, u'').split(u"|")[0])

        return super(Language, self).__getattribute__(attr)

    @property
    def non_capturable_scenario_separator(self):
        return re.sub(r'^[(]', '(?:', self.scenario_separator)

    @classmethod
    def guess_from_string(cls, string):
        # match = re.search(REP.language, string)
        # if match:
        #     instance = cls(match.group(1))
        # else:
        if True:
            instance = cls()

        return instance


class StepDefinition(object):
    """A step definition is a wrapper for user-defined callbacks. It
    gets a few metadata from file, such as filename and line number"""
    def __init__(self, step, function):
        self.function = function
        self.file = fs.relpath(function.func_code.co_filename)
        self.line = function.func_code.co_firstlineno + 1
        self.step = step

    def __call__(self, *args, **kw):
        """Method that actually wrapps the call to step definition
        callback. Sends step object as first argument
        """
        try:
            ret = self.function(self.step, *args, **kw)
            self.step.passed = True
        except AssertionError as e:
            self.step.failed = True
            self.step.why = ReasonToFail(self.step, e)
            raise

        return ret


class Step(parser.Step):
    """ Object that represents each step on feature files."""
    has_definition = False
    indentation = 4
    table_indentation = indentation + 2
    defined_at = None
    why = None
    ran = False
    passed = None
    failed = None
    related_outline = None
    scenario = None
    background = None
    display = True
    columns = None
    matrix = None

    def propose_definition(self):
        sentence = unicode(self.original_sentence)
        method_name = sentence

        groups = [
            ('"', REP.within_double_quotes, r'"([^"]*)"'),
            ("'", REP.within_single_quotes, r"\'([^\']*)\'"),
        ]

        attribute_names = []
        for char, group, template in groups:
            match_groups = group.search(self.original_sentence)
            if match_groups:
                for index, match in enumerate(group.findall(sentence)):
                    sentence = sentence.replace(match, template)
                    group_name = u"group%d" % (index + 1)
                    method_name = method_name.replace(match, group_name)
                    attribute_names.append(group_name)

        method_name = unicodedata.normalize('NFKD', method_name) \
                      .encode('ascii', 'ignore')
        method_name = '%s(step%s)' % (
            "_".join(re.findall("\w+", method_name)).lower(),
            attribute_names and (", %s" % ", ".join(attribute_names)) or "")

        return method_name, sentence

    def _calc_list_length(self, lst):
        length = self.table_indentation + 2
        for item in lst:
            length += strings.column_width(item) + 2

        if len(lst) > 1:
            length += 1

        return length

    def _calc_key_length(self, data):
        return self._calc_list_length(data.keys())

    def _calc_value_length(self, data):
        return self._calc_list_length(data.values())

    @property
    def max_length(self):
        max_length_sentence = strings.column_width(self.sentence) + \
            self.indentation
        max_length_original = strings.column_width(self.original_sentence) + \
            self.indentation

        max_length = max([max_length_original, max_length_sentence])
        for data in self.hashes:
            key_size = self._calc_key_length(data)
            if key_size > max_length:
                max_length = key_size

            value_size = self._calc_value_length(data)
            if value_size > max_length:
                max_length = value_size

        return max_length

    @property
    def parent(self):
        return self.scenario or self.background

    def represent_string(self, string):
        head = ' ' * self.indentation + string
        where = self.described_at

        if self.defined_at:
            where = self.defined_at
        return strings.rfill(head, self.parent.feature.max_length + 1, append=u'# %s:%d\n' % (where.file, where.line))

    def represent_hashes(self):
        lines = strings.dicts_to_string(self.hashes, self.keys).splitlines()
        return u"\n".join([(u" " * self.table_indentation) + line for line in lines]) + "\n"

    def represent_columns(self):
        lines = strings.json_to_string(self.columns, self.non_unique_keys).splitlines()
        return u"\n".join([(u" " * self.table_indentation) + line for line in lines]) + "\n"

    def _get_match(self, ignore_case):
        matched, func = None, lambda: None

        for regex, func in STEP_REGISTRY.items():
            matched = re.search(regex, self.sentence, ignore_case and re.I or 0)
            if matched:
                break

        return matched, StepDefinition(self, func)

    def pre_run(self, ignore_case, with_outline=None):
        matched, step_definition = self._get_match(ignore_case)
        self.related_outline = with_outline

        if not self.defined_at:
            if not matched:
                raise NoDefinitionFound(self)

            self.has_definition = True
            self.defined_at = step_definition

        return matched, step_definition

    def given(self, string):
        return self.behave_as(string)

    def when(self, string):
        return self.behave_as(string)

    def then(self, string):
        return self.behave_as(string)

    def behave_as(self, string):
        """ Parses and runs steps given in string form.

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
        lines = string.split('\n')
        steps = self.many_from_lines(lines)

        if hasattr(self, 'scenario'):
            for step in steps:
                step.scenario = self.scenario

        (_, _, steps_failed, steps_undefined) = self.run_all(steps)
        if not steps_failed and not steps_undefined:
            self.passed = True
            self.failed = False
            return self.passed
        self.passed = False
        self.failed = True
        assert not steps_failed, steps_failed[0].why.exception
        assert not steps_undefined, "Undefined step: %s" % steps_undefined[0].sentence

    def run(self, ignore_case):
        """Runs a step, trying to resolve it on available step
        definitions"""
        matched, step_definition = self.pre_run(ignore_case)
        self.ran = True
        kw = matched.groupdict()

        if kw:
            step_definition(**kw)
        else:
            groups = matched.groups()
            step_definition(*groups)

        self.passed = True
        return True


class Scenario(parser.Scenario):
    """ Object that represents each scenario on feature files."""
    described_at = None
    indentation = 2
    table_indentation = indentation + 2

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

    def run(self, ignore_case, failfast=False):
        """
        Runs a scenario, running each of its steps. Also call
        before_each and after_each callbacks for steps and scenario

        The return value is not the results, but whether or not to keep
        running the tests. The results can be found at self.resultes
        """

        # FIXME: is there an before/after outline hook?
        self.results = []

        if self.outlines:
            generator = self.evaluated
        else:
            generator = ((None, self.steps),)

        for outline, steps in generator:
            call_hook('before_each', 'scenario', self)

            try:
                if self.background:
                    self.background.run(ignore_case)

                # pre-run the steps so we have their definitions set
                for step in steps:
                    try:
                        step.pre_run(ignore_case, with_outline=outline)
                    except NoDefinitionFound:
                        pass

                # run the steps for real
                for step in steps:
                    try:
                        call_hook('before_each', 'step', step)
                        call_hook('before_output', 'step', step)

                        step.run(ignore_case)

                    except (NoDefinitionFound, AssertionError) as e:
                        # we expect steps to assert or not be found
                        if failfast:
                            raise FailFast()

                        break

                    finally:
                        call_hook('after_output', 'step', step)
                        call_hook('after_each', 'step', step)

            except FailFast:
                return False

            finally:
                call_hook('after_each', 'scenario', self)

                if outline:
                    call_hook('outline', 'scenario', self, order, outline,
                            reasons_to_fail)

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

        return True

    def represented(self):
        make_prefix = lambda x: u"%s%s: " % (u' ' * self.indentation, x)
        if self.outlines:
            prefix = make_prefix(self.language.first_of_scenario_outline)
        else:
            prefix = make_prefix(self.language.first_of_scenario)

        head_parts = []
        if self.tags:
            tags = ['@%s' % t for t in self.tags]
            head_parts.append(u' ' * self.indentation)
            head_parts.append(' '.join(tags) + '\n')

        head_parts.append(prefix + self.name)

        head = ''.join(head_parts)
        appendix = ''
        if self.described_at:
            fmt = (self.described_at.file, self.described_at.line)
            appendix = u'# %s:%d\n' % fmt

        max_length = self.max_length
        if self.feature:
            max_length = self.feature.max_length

        return strings.rfill(
            head, max_length + 1,
            append=appendix)

    def represent_examples(self):
        lines = strings.dicts_to_string(self.outlines, self.keys).splitlines()
        return "\n".join([(u" " * self.table_indentation) + line for line in lines]) + '\n'


class Background(parser.Background):
    indentation = 2

    def run(self, ignore_case):
        call_hook('before_each', 'background', self)
        results = []

        for step in self.steps:
            matched, step_definition = step.pre_run(ignore_case)
            call_hook('before_each', 'step', step)
            try:
                results.append(step.run(ignore_case))
            except Exception, e:
                print e
                pass

            call_hook('after_each', 'step', step)

        call_hook('after_each', 'background', self, results)
        return results

    def __repr__(self):
        return '<Background for feature: {0}>'.format(self.feature.name)

    @property
    def max_length(self):
        max_length = 0
        for step in self.steps:
            if step.max_length > max_length:
                max_length = step.max_length

        return max_length

    def represented(self):
        return ((' ' * self.indentation) + 'Background:')


class Feature(parser.Feature):
    """ Object that represents a feature."""

    @classmethod
    def from_string(cls, string):
        """
        Parse a feature from a string

        Hackily cast the classes from the parser class to the core class
        """

        self = parser.Feature.from_string(string)
        # cast to the core class (hacky)
        self.__class__ = cls

        if self.background:
            self.background.__class__ = Background

        for scenario in self.scenarios:
            scenario.__class__ = Scenario

            for step in scenario.steps:
                step.__class__ = Step

        return self

    def get_head(self):
        return u"%s: %s" % (self.language.first_of_feature, self.name)

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
                proceed = scenario.run(ignore_case, failfast=failfast)
                results += scenario.results

                if not proceed:
                    break

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
        sentences = []
        for step in self._proposed_definitions:
            if step.proposed_sentence not in sentences:
                sentences.append(step.proposed_sentence)
                yield step

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
