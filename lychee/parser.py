# -*- coding: utf-8 -*-
# Lychee - Cucumber runner for Python based on Lettuce and Nose
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

"""
A Gherkin parser written using pyparsing
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import range
from builtins import super
from builtins import open
from builtins import chr
from builtins import dict
from builtins import str
from builtins import map
from builtins import zip
from future import standard_library
standard_library.install_aliases()

from codecs import open
from copy import deepcopy
from collections import OrderedDict
from warnings import warn

from pyparsing import (CharsNotIn,
                       col,
                       Group,
                       Keyword,
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
                       stringEnd,
                       Suppress,
                       Word,
                       ZeroOrMore)

from fuzzywuzzy import fuzz

from lychee import fs, languages, strings
from lychee.exceptions import LettuceSyntaxError, LettuceSyntaxWarning


# TODO: is this needed?
memoizedproperty = property


unicodePrintables = u''.join(chr(c) for c in range(65536)
                             if not chr(c).isspace())


class ParseLocation(object):
    """
    The location of a parsed node within the stream
    """

    def __init__(self, parent, s, loc, filename=None):
        self.parent = parent
        self._file = filename
        self.line = lineno(loc, s)
        self.col = col(loc, s)

    def __str__(self):
        return u'{file}:{line}'.format(file=self.file,
                                       line=self.line)

    def __repr__(self):
        return str(self)

    @property
    def file(self):
        """
        Return the relative path to the file
        """

        if self._file:
            # TODO: Lettuce has this pluggable, for unit testing
            return fs.FileSystem().relpath(self._file)
        elif self.parent:
            if self.parent.feature.described_at is self:
                return None
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

    def represented(self, indent=0, annotate=True):
        """
        Return a representation of the node
        """

        s = u' ' * indent + self.text.strip()

        if annotate:
            s = strings.ljust(s, self.feature.max_length + 1) + \
                u'# ' + str(self.described_at)

        return s


class Step(Node):
    """
    A statement
    """

    def __init__(self, s, loc, tokens):

        super().__init__(s, loc, tokens)

        # statements are made up of a statement sentence + optional data
        # the optional data can either be a table or a multiline string
        token = tokens[0]

        self.sentence = u' '.join(token.sentence)
        self.table = list(map(list, token.table)) \
            if token.table else None
        self.multiline = token.multiline

    def __str__(self):
        return '<Step: "%s">' % self.sentence

    def __repr__(self):
        return str(self)

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

        try:
            return self.scenario.feature
        except AttributeError:
            return self.background.feature

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
            strings.get_terminal_width(self.represented(annotate=False)),
            *[strings.get_terminal_width(line)
              for line in self.represent_hashes().splitlines()]
        )

    def represented(self, indent=4, annotate=True):
        """
        Represent the line
        """

        return super().represented(indent=indent, annotate=annotate)

    def represent_hashes(self, indent=6, **kwargs):
        """
        Render the table
        """

        return strings.represent_table(self.table, indent=indent, **kwargs)

    def resolve_substitutions(self, outline):
        """
        Creates a copy of the step with any <variables> resolved
        """

        self = deepcopy(self)

        for key, value in outline.items():
            key = u'<{key}>'.format(key=key)

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
        super().__init__(*args)

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

    def represented(self, indent=2, annotate=True):
        """
        Include block indents
        """

        return super().represented(indent=indent, annotate=annotate)


class TaggedBlock(Block):
    """
    Tagged blocks contain type-specific child content as well as tags
    """
    def __init__(self, s, loc, tokens):
        super().__init__(s, loc, tokens)

        token = tokens[0]

        self._tags = list(token.tags)
        self.keyword = token.keyword
        self.name = token.name.strip()

        if self.name == '':
            raise LettuceSyntaxError(
                None,
                "{line}:{col} {klass} must have a name".format(
                    line=lineno(loc, s),
                    col=col(loc, s),
                    klass=self.__class__.__name__))

    def __str__(self):
        return '<{klass}: "{name}">'.format(
            # FIXME: use self.language
            klass=self.__class__.__name__,
            name=self.name)

    def __repr__(self):
        return str(self)

    @property
    def tags(self):
        return self._tags

    def represented(self, indent=0, annotate=True):
        """
        Reresent a tagged block
        """

        s = u' ' * indent + u'{keyword}: {name}'.format(keyword=self.keyword,
                                                        name=self.name)
        if annotate:
            s = strings.ljust(s, self.feature.max_length + 1) + \
                u'# ' + str(self.described_at)

        return s

    def represent_tags(self, indent=0):
        """
        Represent the tags of a tagged block
        """

        return u' ' * indent + u'  '.join(u'@%s' % tag for tag in self.tags)

    def matches_tags(self, tags):
        """
        Return true if the TaggedBlock contains all of the tags specified
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
    def add_statements(cls, tokens):
        token = tokens[0]

        self = super().add_statements(tokens)

        # Build a list of outline hashes
        # A single scenario can have multiple example blocks, the returned
        # token is a list of TABLE tokens
        self.outlines = []

        for outline in token.outlines:
            outlines = list(map(list, outline))

            # the first row of the table is the column headings
            keys = outlines[0]

            self.outlines += [
                OrderedDict(zip(keys, row))
                for row in outlines[1:]
            ]

        return self

    def represented(self, indent=2, **kwargs):
        return super().represented(indent=indent, **kwargs)

    def represent_outlines(self, indent=4):
        """
        Render the outlines table
        """

        return strings.represent_table(self.outlines_table, indent=indent)

    @memoizedproperty
    def max_length(self):
        """
        The max length of the feature, description and child blocks
        """

        return max(
            0,
            strings.get_terminal_width(self.represented(annotate=False)),
            *([step.max_length for step in self.steps] +
              [strings.get_terminal_width(line)
               for line in self.represent_outlines().splitlines()])
        )

    @memoizedproperty
    def outlines_table(self):
        """
        Return the outlines as a table
        """

        # get the list of column headings
        headings = OrderedDict()

        for outline in self.outlines:
            headings.update(outline)

        headings = list(headings.keys())
        table = [headings]

        # append the data to the table
        for outline in self.outlines:
            table.append([outline.get(cell, '') for cell in headings])

        return table

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

        super().__init__(s, loc, tokens)

        token = tokens[0]

        self.lines = [u' '.join(line).strip() for line in token]

    def __str__(self):
        return u'\n'.join(self.lines)

    def __repr__(self):
        return str(self)

    def represented(self, indent=2, annotate=True):
        return u'\n'.join(
            self.represent_line(n)
            for n, _ in enumerate(self.lines)
        )

    def represent_line(self, n, indent=2, annotate=True):
        """
        Represent the nth line in the description
        """

        line = self.lines[n]
        s = u' ' * indent + line

        if annotate:
            s = strings.ljust(s, self.feature.max_length + 1) + \
                u'# {file}:{line}'.format(
                    file=self.described_at.file,
                    line=self.description_at[n])

        return s

    @memoizedproperty
    def description_at(self):
        """
        Return a tuple of lines in the string containing the description
        """

        offset = self.described_at.line

        return tuple(offset + lineno for lineno, _
                     in enumerate(self.lines))

    @memoizedproperty
    def max_length(self):
        try:
            return max(strings.get_terminal_width(
                self.represent_line(n, annotate=False))
                for n, _ in enumerate(self.lines))
        except ValueError:
            return 0


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
        self.description_node = token.description
        # this is here for legacy compatability
        self.described_at.description_at = token.description.description_at

        self.background = token.background \
            if isinstance(token.background, Background) else None
        self.scenarios = list(token.scenarios)

        # add the back references
        self.description_node.feature = self

        if self.background:
            self.background.feature = self

        for scenario in self.scenarios:
            scenario.feature = self

        return self

    @property
    def description(self):
        """
        In order to remain compatible with the existing API we disassemble
        the Description node
        """
        return str(self.description_node)

    @property
    def feature(self):
        """
        Convenience property for generic functions
        """

        return self

    @memoizedproperty
    def max_length(self):
        """
        The max length of the feature, description and child blocks
        """

        return max(
            0,
            strings.get_terminal_width(
                self.represented(annotate=False, description=False)),
            self.description_node.max_length,
            *[scenario.max_length for scenario in self.scenarios]
        )

    def represented(self, indent=0, annotate=True, description=True):
        s = super().represented(indent=indent, annotate=annotate)

        # FIXME: indent here is description default indent + feature
        # requested indent
        if description and self.description != '':
            s += u'\n'
            s += self.description_node.represented(annotate=annotate)

        return s

    def represent_description(self, **kwargs):
        return self.description_node.represented(**kwargs)


def guess_language(string=None, filename=None):
    """
    Attempt to guess the language

    Do this by parsing the comments at the top of the file for the

        # language: fr

    phrase.
    """

    LANG_PARSER = ZeroOrMore(
        Suppress('#') + (
            ((Suppress(Keyword('language')) + Suppress(':') +
              Word(unicodePrintables)('language')) |
             Suppress(restOfLine))
        )
    )

    try:
        if string:
            tokens = LANG_PARSER.parseString(string)
        elif filename:
            with open(filename, 'r', 'utf-8') as fp:
                tokens = LANG_PARSER.parseFile(fp)
        else:
            raise RuntimeError("Must pass string or filename")

        code = tokens.language

        if code != '':
            return languages.Language(code=code)

    except ParseException:
        # try English
        pass

    return languages.English()


def parse(string=None, filename=None, token=None, lang=None):
    """
    Parse a token stream from or raise a SyntaxError

    This function includes the parser grammar.
    """

    if not lang:
        lang = guess_language(string, filename)

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
        elif token == r'\\':
            return u'\\'

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
    def clean_multiline_string(s, loc, tokens):
        """
        Clean a multiline string

        The indent level of a multiline string is the indent level of the
        triple-". We have to derive this by walking backwards from the
        location of the quoted string token to the newline before it.

        We also want to remove the leading and trailing newline if they exist.

        FIXME: assumes UNIX newlines
        """

        def remove_indent(multiline, indent):
            """
            Generate the lines removing the indent
            """

            for ln in multiline.splitlines():
                if ln and not ln[:indent].isspace():
                    warn("%s: %s: under-indented multiline string "
                         "truncated: '%s'" %
                         (lineno(loc, s), col(loc, s), ln),
                         LettuceSyntaxWarning)

                # for those who are surprised by this, slicing a string
                # shorter than indent will yield empty string, not IndexError
                yield ln[indent:]

        # determine the indentation offset
        indent = loc - s.rfind('\n', 0, loc) - 1

        multiline = '\n'.join(remove_indent(tokens[0], indent))

        # remove leading and trailing newlines
        if multiline[0] == '\n':
            multiline = multiline[1:]

        if multiline[-1] == '\n':
            multiline = multiline[:-1]

        return multiline

    MULTILINE = QuotedString('"""', multiline=True)
    MULTILINE.setParseAction(clean_multiline_string)

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
        lang.BACKGROUND('keyword') + Suppress(':') + EOL
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
        lang.SCENARIO('keyword') + Suppress(':') +
        restOfLine('name') +
        EOL
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
        lang.FEATURE('keyword') + Suppress(':') +
        restOfLine('name') +
        EOL
    )
    FEATURE_DEFN.setParseAction(Feature)

    #
    # A description composed of zero or more lines, before the
    # Background/Scenario block
    #
    DESCRIPTION_LINE = Group(
        ~BACKGROUND_DEFN + ~SCENARIO_DEFN +
        OneOrMore(UTFWORD).setWhitespaceChars(' \t') +
        EOL
    )
    DESCRIPTION = Group(ZeroOrMore(DESCRIPTION_LINE | EOL))
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
        if e.parserElement == stringEnd:
            msg = "Expected EOF (max one feature per file)"
        else:
            msg = e.msg

        raise LettuceSyntaxError(
            filename,
            u"{lineno}:{col} Syntax Error: {msg}\n{line}\n{space}^".format(
                msg=msg,
                lineno=e.lineno,
                col=e.col,
                line=e.line,
                space=' ' * (e.col - 1)))
    except LettuceSyntaxError as e:
        # reraise the exception with the filename
        raise LettuceSyntaxError(filename, e.string)
