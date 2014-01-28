# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
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
#
"""
A Gherkin parser written using pyparsing
"""

from copy import deepcopy
from textwrap import dedent

from pyparsing import (CharsNotIn,
                       col,
                       Group,
                       Keyword,
                       lineEnd,
                       lineStart,
                       lineno,
                       OneOrMore,
                       Optional,
                       ParseException,
                       ParserElement,
                       printables,
                       pythonStyleComment,
                       QuotedString,  # function
                       quotedString,  # token
                       restOfLine,
                       SkipTo,
                       stringEnd,
                       Suppress,
                       White,
                       Word,
                       ZeroOrMore)

from fuzzywuzzy import fuzz

from lettuce.exceptions import LettuceSyntaxError


class Step(object):
    """
    A statement
    """

    def __init__(self, s, loc, tokens):

        # statements are made up of a statement sentence + optional data
        # the optional data can either be a table or a multiline string
        token = tokens[0]

        self.sentence = ' '.join(token.sentence)
        self.table = map(list, token.table) \
            if token.table else None
        self.multiline = dedent(str(token.multiline)).strip() \
            if token.multiline else None

    def __unicode__(self):
        return u'<Step: "%s">' % self.sentence

    def __repr__(self):
        return unicode(self).encode('utf-8')

    @property
    def keys(self):
        """
        Return the first row of a table if this statement contains one
        """
        if self.table:
            return tuple(self.table[0])
        else:
            return []

    @property
    def hashes(self):
        """
        Return the table attached to the step as a list of hashes, where the
        first row is the column headings
        """

        if not self.table:
            return []

        keys = self.keys

        return [
            dict(zip(keys, row))
            for row in self.table[1:]
        ]

    def resolve_substitutions(self, outline):
        """
        Creates a copy of the step with any <variables> resolved
        """

        self = deepcopy(self)

        for key, value in outline.items():
            key = '<{key}>'.format(key=key)

            self.sentence = self.sentence.replace(key, value)

            if self.multiline:
                self.multiline = self.multiline.replace(key, value)

            if self.table:
                for i, row in enumerate(self.table):
                    for j, cell in enumerate(row):
                        self.table[i][j] = cell.replace(key, value)

        return self


class Block(object):
    """
    A generic block, e.g. Feature:, Scenario:

    Blocks contain a number of statements
    """

    def __init__(self, tokens):
        self.statements = []

    @classmethod
    def add_statements(cls, tokens):
        """
        Consume the statements to add to this block
        """

        token = tokens[0]

        self = token.node
        self.steps = list(token.statements)

        # add a backreference
        for step in self.steps:
            setattr(step, self.__class__.__name__.lower(), self)

        assert all(isinstance(statement, Step)
                   for statement in self.steps)

        return self


class TaggedBlock(Block):
    """
    Tagged blocks contain type-specific child content as well as tags
    """
    def __init__(self, s, loc, tokens):
        super(TaggedBlock, self).__init__(tokens)

        token = tokens[0]

        self._tags = list(token.tags)
        self.name = token.name.strip()

        if self.name == '':
            raise LettuceSyntaxError(
                None,
                "{line}:{col} {klass} must have a name".format(
                    line=lineno(loc, s),
                    col=col(loc, s),
                    klass=self.__class__.__name__))

    def __unicode__(self):
        return '<{klass}: "{name}">'.format(
            # FIXME: use self.language
            klass=self.__class__.__name__,
            name=self.name)

    def __repr__(self):
        return unicode(self).encode('utf-8')

    @property
    def tags(self):
        return self._tags

    def matches_tags(self, tags):
        """
        Return true of the TaggedBlock contains all of the tags specified
        by tags AND does not contain any of the excluded tags AND
        matches any 'fuzzy' tags
        """

        our_tags = set(self.tags)

        fuzzy_required_tags = set(tag[1:] for tag in tags
                                  if tag.startswith('~'))
        fuzzy_unwanted_tags = set(tag[2:] for tag in tags
                                  if tag.startswith('-~'))
        unwanted_tags = set(tag[1:] for tag in tags
                            if tag.startswith('-'))
        required_tags = set(tag for tag in tags
                            if not tag.startswith('-')
                            and not tag.startswith('~'))

        # at least one of the required tags should appear in ours tags (i.e.
        # the intersection is not {})
        # the unwanted tags should be a disjoint set (i.e. intersection is {})
        if (required_tags and required_tags.isdisjoint(our_tags)) or \
           not unwanted_tags.isdisjoint(our_tags):
            # if either case isn't true, don't even attempt the fuzzy matching
            return False

        # apply fuzzy matches
        #
        # all required fuzzy tags must have an 80% match to at least
        # one of our tags
        fuzzy_matches = \
            all(any(fuzz.ratio(tag, our_tag) > 80 for our_tag in our_tags)
                for tag in fuzzy_required_tags)

        # unwanted fuzzy tags must have a <= 80% match to all of our tags
        fuzzy_unwanted = \
            all(fuzz.ratio(tag, our_tag) <= 80
                for tag in fuzzy_unwanted_tags
                for our_tag in our_tags)

        return fuzzy_matches and fuzzy_unwanted


class Background(Block):
    pass


class Scenario(TaggedBlock):
    @classmethod
    def add_statements(cls, s, loc, tokens):
        token = tokens[0]

        self = super(Scenario, cls).add_statements(tokens)

        # Build a list of outline hashes
        # A single scenario can have multiple example blocks, the returned
        # token is a list of TABLE tokens
        self.outlines = []

        for outline in token.outlines:
            outlines = map(list, outline)

            # the first row of the table is the column headings
            keys = outlines[0]

            self.outlines += [
                dict(zip(keys, row))
                for row in outlines[1:]
            ]

        return self

    @property
    def tags(self):
        return self._tags + self.feature.tags

    @property
    def solved_steps(self):
        """
        Return a list of the steps, with any outline substitutions applied
        """

        if not self.outlines:
            return self.steps

        if hasattr(self, '_solved_steps'):
            return self._solved_steps

        steps = [step.resolve_substitutions(outline)
                 for outline in self.outlines
                 for step in self.steps]

        # set a backref to the scenario
        for step in steps:
            step.scenario = self

        self._solved_steps = steps

        return steps

    @property
    def evaluated(self):
        """
        Yield the outline and steps

        FIXME: why do we have both this and solved steps?
        """

        for outline in self.outlines:
            steps = [step.resolve_substitutions(outline)
                     for step in self.steps]

            # set a backref to the scenario
            for step in steps:
                step.scenario = self

            yield (outline, steps)


class Feature(TaggedBlock):
    @classmethod
    def add_blocks(cls, tokens):
        """
        Add the background and other blocks to the feature
        """

        token = tokens[0]

        self = token.node
        self.description = '\n'.join(line.strip()
                                     for line
                                     in token.description[0].split('\n'))\
            .strip()
        self.background = token.background \
            if isinstance(token.background, Background) else None
        self.scenarios = list(token.scenarios)

        # add the back references
        if self.background:
            self.background.feature = self

        for scenario in self.scenarios:
            scenario.feature = self

        return self


"""
End of Line
"""
EOL = Suppress(lineEnd)

"""
@tag
"""
TAG = Suppress('@') + Word(printables)

"""
A table
"""
TABLE_ROW = Suppress('|') + OneOrMore(CharsNotIn('|\n') + Suppress('|')) + EOL
TABLE_ROW.setParseAction(lambda tokens: [v.strip() for v in tokens])
TABLE = Group(OneOrMore(Group(TABLE_ROW)))

"""
Multiline string
"""
MULTILINE = QuotedString('"""', multiline=True)

"""
A Step

Steps begin with a keyword such as Given, When, Then or And
They can contain an optional inline comment, although it's possible to
encapsulate it in a string. Finally they can contain a table or a multiline
'Python' string.

<variables> are not parsed as part of the grammar as it's not easy to
distinguish between a variable and XML. Instead scenarios will replace
instances in the steps based on the outline keys.
"""
STATEMENT_KEYWORD = \
    Keyword('Given') | \
    Keyword('When') | \
    Keyword('Then') | \
    Keyword('And')

STATEMENT_SENTENCE = Group(
    STATEMENT_KEYWORD +
    OneOrMore(Word(printables).setWhitespaceChars(' \t') |
              quotedString.setWhitespaceChars(' \t')) +
    EOL
)

STATEMENT = Group(
    STATEMENT_SENTENCE('sentence') +
    Optional(TABLE('table') | MULTILINE('multiline'))
)
STATEMENT.setParseAction(Step)

STATEMENTS = Group(ZeroOrMore(STATEMENT))

"""
Background:
"""
BACKGROUND_DEFN = \
    Suppress(Keyword('Background') + ':' + EOL)
BACKGROUND_DEFN.setParseAction(Background)

BACKGROUND = Group(
    BACKGROUND_DEFN('node') +
    STATEMENTS('statements')
)
BACKGROUND.setParseAction(Background.add_statements)

"""
Scenario: description
"""
SCENARIO_DEFN = Group(
    Group(ZeroOrMore(TAG))('tags') +
    Suppress((Keyword('Scenario') + Optional(Keyword('Outline'))) +
             ':') +
    restOfLine('name')
)
SCENARIO_DEFN.setParseAction(Scenario)

SCENARIO = Group(
    SCENARIO_DEFN('node') +
    STATEMENTS('statements') +
    Group(ZeroOrMore(
        Suppress(Keyword('Examples') + ':') + EOL + TABLE
    ))('outlines')
)
SCENARIO.setParseAction(Scenario.add_statements)

"""
Feature: description
"""
FEATURE_DEFN = Group(
    Group(ZeroOrMore(TAG))('tags') +
    Suppress(Keyword('Feature') + ':') +
    restOfLine('name')
)
FEATURE_DEFN.setParseAction(Feature)


"""
Complete feature file definition
"""
FEATURE = Group(
    FEATURE_DEFN('node') +
    Group(SkipTo(BACKGROUND | SCENARIO))('description') +
    Optional(BACKGROUND('background')) +
    Group(OneOrMore(SCENARIO))('scenarios') +
    stringEnd)
FEATURE.ignore(pythonStyleComment)
FEATURE.setParseAction(Feature.add_blocks)


def from_string(cls, string):
    """
    Parse a Feature object from a string
    """

    try:
        tokens = FEATURE.parseString(string)
        return tokens[0]
    except ParseException as e:
        raise LettuceSyntaxError(
            None,
            "{lineno}:{col} Syntax Error: {msg}\n{line}\n{space}^".format(
                msg=e.msg,
                lineno=e.lineno,
                col=e.col,
                line=e.line,
                space=' ' * (e.col - 1)))

Feature.from_string = classmethod(from_string)
