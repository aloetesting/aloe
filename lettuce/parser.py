"""
A Gherkin parser written using pyparsing
"""

from pyparsing import (CharsNotIn,
                       Group,
                       Keyword,
                       lineEnd,
                       OneOrMore,
                       Optional,
                       ParseException,
                       printables,
                       pythonStyleComment,
                       QuotedString,
                       restOfLine,
                       SkipTo,
                       stringEnd,
                       Suppress,
                       White,
                       Word,
                       ZeroOrMore)


class Statement(object):
    """
    A statement
    """

    def __init__(self, tokens):

        # statements are made up of a statement sentence + optional data
        # the optional data can either be a table or a multiline string
        try:
            keyword, remainder, data = tokens
        except ValueError:
            keyword, remainder = tokens
            data = None

        self.sentence = keyword + remainder
        self.table = None
        self.multiline = None

        if hasattr(data, 'table'):
            self.table = map(list, data)
        else:
            self.multiline = data

    def __repr__(self):
        r = 'Statement'

        if self.table:
            r += '+Table'
        elif self.multiline:
            r += '+Multiline'

        r += '<%s>' % self.statement

        return r

    @property
    def keys(self):
        """
        Return the first row of a table if this statement contains one
        """
        return tuple(self.table[0])

    @property
    def hashes(self):
        keys = self.keys

        return [
            dict(zip(keys, row))
            for row in self.table[1:]
        ]


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

        assert all(isinstance(statement, Statement)
                   for statement in self.steps)

        return self


class TaggedBlock(Block):
    """
    Tagged blocks contain type-specific child content as well as tags
    """
    def __init__(self, tokens):
        super(TaggedBlock, self).__init__(tokens)

        token = tokens[0]

        self._tags = list(token.tags)
        self.name = token.name

    def __repr__(self):
        return '<{klass}: "{name}">'.format(
            klass=self.__class__.__name__,
            name=self.name)

    @property
    def tags(self):
        return self._tags


class Background(Block):
    pass


class Scenario(TaggedBlock):
    @classmethod
    def add_statements(cls, tokens):
        token = tokens[0]

        self = super(Scenario, cls).add_statements(tokens)

        self.examples = token.examples

        return self

    @property
    def tags(self):
        return self._tags + self.feature.tags


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
TABLE = Group(OneOrMore(Group(TABLE_ROW)))('table')

"""
Multiline string
"""
MULTILINE = QuotedString('"""', multiline=True)

"""
Statement
"""
BLOCK_DESC = Suppress('*') + restOfLine

STATEMENT_KEYWORD = \
    Keyword('Given') | \
    Keyword('When') | \
    Keyword('Then') | \
    Keyword('And')


STATEMENT = \
    STATEMENT_KEYWORD + \
    restOfLine + \
    Optional(TABLE | MULTILINE)
STATEMENT.setParseAction(Statement)

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
             ':' + White()) +
    restOfLine('name')
)
SCENARIO_DEFN.setParseAction(Scenario)

SCENARIO = Group(
    SCENARIO_DEFN('node') +
    STATEMENTS('statements') +
    Optional(Suppress(Keyword('Examples') + ':') + EOL + TABLE('examples'))
)
SCENARIO.setParseAction(Scenario.add_statements)

"""
Feature: description
"""
FEATURE_DEFN = Group(
    Group(ZeroOrMore(TAG))('tags') +
    Suppress(Keyword('Feature') + ':' + White()) +
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
        print "Syntax Error, line", e.lineno
        print e.line
        print " " * (e.column - 1) + "^"

        print e.parserElement
        print e.pstr
        raise

Feature.from_string = classmethod(from_string)
