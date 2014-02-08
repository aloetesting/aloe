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

from codecs import open
from copy import deepcopy
from textwrap import dedent

from pyparsing import (CharsNotIn,
                       col,
                       Group,
                       line,
                       lineEnd,
                       lineno,
                       OneOrMore,
                       Optional,
                       ParseException,
                       pythonStyleComment,
                       QuotedString,  # function
                       quotedString,  # token
                       restOfLine,
                       SkipTo,
                       stringEnd,
                       Suppress,
                       Word,
                       ZeroOrMore)

from fuzzywuzzy import fuzz

from lettuce import languages, strings
from lettuce.exceptions import LettuceSyntaxError
from lettuce.decorators import memoizedproperty


unicodePrintables = u''.join(unichr(c) for c in xrange(65536)
                             if not unichr(c).isspace())


class ParseLocation(object):
    """
    The location of a parsed node within the stream
    """

    def __init__(self, parent, s, loc, filename=None):
        self.parent = parent
        self._file = filename
        self.line = lineno(loc, s)
        self.col = col(loc, s)

    def __repr__(self):
        return '(%s, %s)' % (self.line, self.col)

    @property
    def file(self):
        """
        Return the relative path to the file
        """

        # need to import this here to prevent a circular import
        from lettuce.core import fs

        if self._file:
            return fs.relpath(self._file)
        elif self.parent:
            return self.parent.feature.described_at.file
        else:
            return None

    @file.setter
    def file(self, value):
        self._file = value


class Node(object):
    """
    A parse node
    """

    def __init__(self, s, loc, tokens):
        self.described_at = ParseLocation(self, s, loc)
        self.text = line(loc, s)

    def represented(self):
        """
        Return a representation of the node
        """

        return self.text


class Step(Node):
    """
    A statement
    """

    def __init__(self, s, loc, tokens):

        super(Step, self).__init__(s, loc, tokens)

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

    @classmethod
    def parse_steps_from_string(cls, string, language=None):
        """
        Parse a number of steps, returns a list of steps

        This is used by step.behave_as
        """

        tokens = parse(string=string, token='STATEMENTS', lang=language)

        return list(tokens[0])

    @property
    def feature(self):
        """
        The feature this step is a part of
        """

        return self.scenario.feature

    @memoizedproperty
    def keys(self):
        """
        Return the first row of a table if this statement contains one
        """
        if self.table:
            return tuple(self.table[0])
        else:
            return []

    @memoizedproperty
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

    @memoizedproperty
    def max_length(self):
        """
        The max length of the feature, description and child blocks
        """

        return max(
            0,
            len(self.represented()),
            *[len(line) for line in self.represent_hashes().splitlines()]
        )

    def represent_hashes(self, indent=6):
        """
        Render the table
        """

        return strings.represent_table(self.table, indent=indent)

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


class Block(Node):
    """
    A generic block, e.g. Feature:, Scenario:

    Blocks contain a number of statements
    """

    def __init__(self, *args):
        super(Block, self).__init__(*args)

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

    def represented(self, indent=2):
        """
        Include block indents
        """

        return u' ' * indent + super(Block, self).represented().strip()


class TaggedBlock(Block):
    """
    Tagged blocks contain type-specific child content as well as tags
    """
    def __init__(self, s, loc, tokens):
        super(TaggedBlock, self).__init__(s, loc, tokens)

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

    @memoizedproperty
    def max_length(self):
        """
        The max length of the feature, description and child blocks
        """

        return max(
            len(self.represented()),
            *[step.max_length for step in self.steps]
        )

    @property
    def tags(self):
        return self._tags + self.feature.tags

    @property
    def evaluated(self):
        """
        Yield the outline and steps
        """

        for outline in self.outlines:
            steps = [step.resolve_substitutions(outline)
                     for step in self.steps]

            # set a backref to the scenario
            for step in steps:
                step.scenario = self

            yield (outline, steps)

    @memoizedproperty
    def solved_steps(self):
        """
        DO NOT USE: Used only in the tests.
        """

        all_steps = []

        for _, steps in self.evaluated:
            all_steps += steps

        return all_steps


class Description(Node):
    """
    The description block of a feature
    """

    def __init__(self, s, loc, tokens):

        super(Description, self).__init__(s, loc, tokens)

        token = tokens[0]

        self.description = u'\n'.join(u' '.join(line)
                                      for line in token).strip()

    def __unicode__(self):
        return self.description

    def __repr__(self):
        return unicode(self)


class Feature(TaggedBlock):
    @classmethod
    def from_string(cls, string, language=None):
        """
        Returns a Feature from a string
        """

        return parse(string=string, token='FEATURE', lang=language)[0]

    @classmethod
    def from_file(cls, filename, language=None):
        """
        Parse a file or filename
        """

        self = parse(filename=filename, token='FEATURE', lang=language)[0]
        self.described_at.file = filename
        return self

    @classmethod
    def add_blocks(cls, tokens):
        """
        Add the background and other blocks to the feature
        """

        token = tokens[0]

        self = token.node
        #
        # In order to remain compatible with the existing API we disassemble
        # the Description node
        #
        self.description = unicode(token.description)
        # FIXME: this is not at all right
        self.described_at.description_at = (
            token.description.described_at.line,
            token.description.described_at.col)

        self.background = token.background \
            if isinstance(token.background, Background) else None
        self.scenarios = list(token.scenarios)

        # add the back references
        if self.background:
            self.background.feature = self

        for scenario in self.scenarios:
            scenario.feature = self

        return self

    @memoizedproperty
    def max_length(self):
        """
        The max length of the feature, description and child blocks
        """

        return max(
            len(self.text),
            *[scenario.max_length for scenario in self.scenarios]
        )

    def represented(self):
        return Node.represented(self)


def parse(string=None, filename=None, token=None, lang=None):
    """
    Attempt to parse a token stream from a string or raise a SyntaxError

    This function includes the parser grammar.
    """

    if not lang:
        lang = languages.English()

    #
    # End of Line
    #
    EOL = Suppress(lineEnd)
    UTFWORD = Word(unicodePrintables)

    #
    # @tag
    #
    TAG = Suppress('@') + UTFWORD

    #
    # A table
    #
    # A table is made up of rows of cells, e.g.
    #
    #   | column 1 | column 2 |
    #
    # Table cells need to be able to handle escaped tokens such as \| and \n
    #
    def handle_esc_char(tokens):
        token = tokens[0]

        if token == r'\|':
            return u'|'
        elif token == r'\n':
            return u'\n'

        raise NotImplementedError(u"Unknown token: %s" % token)

    ESC_CHAR = Word(initChars=r'\\', bodyChars=unicodePrintables, exact=2)
    ESC_CHAR.setParseAction(handle_esc_char)

    #
    # A cell can contain anything except a cell marker, new line or the
    # beginning of a cell marker, we then handle escape characters separately
    # and recombine the cell afterwards
    #
    CELL = OneOrMore(CharsNotIn('|\n\\') + Optional(ESC_CHAR))
    CELL.setParseAction(lambda tokens: u''.join(tokens))

    TABLE_ROW = Suppress('|') + OneOrMore(CELL + Suppress('|')) + EOL
    TABLE_ROW.setParseAction(lambda tokens: [v.strip() for v in tokens])
    TABLE = Group(OneOrMore(Group(TABLE_ROW)))

    #
    # Multiline string
    #
    MULTILINE = QuotedString('"""', multiline=True)

    # A Step
    #
    # Steps begin with a keyword such as Given, When, Then or And They can
    # contain an optional inline comment, although it's possible to encapsulate
    # it in a string. Finally they can contain a table or a multiline 'Python'
    # string.
    #
    # <variables> are not parsed as part of the grammar as it's not easy to
    # distinguish between a variable and XML. Instead scenarios will replace
    # instances in the steps based on the outline keys.
    #
    STATEMENT_SENTENCE = Group(
        lang.STATEMENT +  # Given, When, Then, And
        OneOrMore(UTFWORD.setWhitespaceChars(' \t') |
                  quotedString.setWhitespaceChars(' \t')) +
        EOL
    )

    STATEMENT = Group(
        STATEMENT_SENTENCE('sentence') +
        Optional(TABLE('table') | MULTILINE('multiline'))
    )
    STATEMENT.setParseAction(Step)

    STATEMENTS = Group(ZeroOrMore(STATEMENT))

    #
    # Background:
    #
    BACKGROUND_DEFN = \
        Suppress(lang.BACKGROUND + ':' + EOL)
    BACKGROUND_DEFN.setParseAction(Background)

    BACKGROUND = Group(
        BACKGROUND_DEFN('node') +
        STATEMENTS('statements')
    )
    BACKGROUND.setParseAction(Background.add_statements)

    #
    # Scenario: description
    #
    SCENARIO_DEFN = Group(
        Group(ZeroOrMore(TAG))('tags') +
        Suppress(lang.SCENARIO + ':') +
        restOfLine('name')
    )
    SCENARIO_DEFN.setParseAction(Scenario)

    SCENARIO = Group(
        SCENARIO_DEFN('node') +
        STATEMENTS('statements') +
        Group(ZeroOrMore(
            Suppress(lang.EXAMPLES + ':') + EOL + TABLE
        ))('outlines')
    )
    SCENARIO.setParseAction(Scenario.add_statements)

    #
    # Feature: description
    #
    FEATURE_DEFN = Group(
        Group(ZeroOrMore(TAG))('tags') +
        Suppress(lang.FEATURE + ':') +
        restOfLine('name')
    )
    FEATURE_DEFN.setParseAction(Feature)

    #
    # A description composed of zero or more lines, before the
    # Background/Scenario block
    #
    DESCRIPTION = Group(
        ZeroOrMore(
            ~SCENARIO_DEFN + ~BACKGROUND_DEFN +
            Group(ZeroOrMore(UTFWORD)) + EOL
        )
    )
    DESCRIPTION.setParseAction(Description)

    #
    # Complete feature file definition
    #
    FEATURE = Group(
        FEATURE_DEFN('node') +
        DESCRIPTION('description') +
        Optional(BACKGROUND('background')) +
        Group(OneOrMore(SCENARIO))('scenarios') +
        stringEnd)
    FEATURE.ignore(pythonStyleComment)
    FEATURE.setParseAction(Feature.add_blocks)

    #
    # Try parsing the string
    #

    if not token:
        token = FEATURE
    else:
        token = locals()[token]

    try:
        if string:
            tokens = token.parseString(string)
        elif filename:
            with open(filename, 'r', 'utf-8') as fp:
                tokens = token.parseFile(fp)
        else:
            raise RuntimeError("Must pass string or filename")

        return tokens
    except ParseException as e:
        raise LettuceSyntaxError(
            filename,
            u"{lineno}:{col} Syntax Error: {msg}\n{line}\n{space}^".format(
                msg=e.msg,
                lineno=e.lineno,
                col=e.col,
                line=e.line,
                space=' ' * (e.col - 1)))
