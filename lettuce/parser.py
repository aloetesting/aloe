"""
A Gherkin parser written using pyparsing
"""

from pyparsing import (CharsNotIn,
                       Group,
                       Keyword,
                       lineEnd,
                       OneOrMore,
                       Optional,
                       printables,
                       QuotedString,
                       restOfLine,
                       SkipTo,
                       stringEnd,
                       Suppress,
                       White,
                       Word,
                       ZeroOrMore)


class Tag(object):
    """
    A tag

    @tag
    """
    def __init__(self, tokens):
        self.tag = tokens[0]

    def __repr__(self):
        return '{klass}<{tag}>'.format(klass=self.__class__.__name__,
                                       tag=self.tag)


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

        self.statement = keyword + remainder
        self.table = None
        self.multiline = None

        if hasattr(data, 'table'):
            self.table = data
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


class Block(object):
    """
    A generic block, e.g. Feature:, Scenario:

    Blocks contain a number of statements
    """

    def __init__(self, tokens):
        self.statements = []

    def __repr__(self):
        return '{klass}<{n} statements>'.format(klass=self.__class__.__name__,
                                                n=len(self.statements))

    @classmethod
    def add_statements(cls, tokens):
        """
        Consume the statements to add to this block
        """

        token = tokens[0]

        self = token.node
        self.statements = token.statements

        assert all(isinstance(statement, Statement)
                   for statement in self.statements)

        return self


class TaggedBlock(Block):
    """
    Tagged blocks contain type-specific child content as well as tags
    """
    def __init__(self, tokens):
        super(TaggedBlock, self).__init__(tokens)

        token = tokens[0]

        self.tags = token.tags
        self.name = token.name

        assert all(isinstance(tag, Tag) for tag in self.tags)

    def __repr__(self):
        return '{klass}<{tag}>'.format(
            klass=self.__class__.__name__,
            tag=','.join([self.name] +
                         [' @%s' % tag.tag for tag in self.tags]))


class Background(Block):
    pass


class Scenario(TaggedBlock):
    @classmethod
    def add_statements(cls, tokens):
        token = tokens[0]

        self = super(Scenario, cls).add_statements(tokens)

        self.examples = token.examples

        return self


class Feature(TaggedBlock):
    @classmethod
    def add_blocks(cls, tokens):
        """
        Add the background and other blocks to the feature
        """

        token = tokens[0]

        self = token.node
        self.background = token.background
        self.scenarios = token.scenarios

        return self


"""
End of Line
"""
EOL = Suppress(lineEnd)

"""
@tag
"""
TAG = Suppress('@') + Word(printables) + EOL
TAG.setParseAction(Tag)

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
STATEMENT = \
    (Keyword('Given') | Keyword('When') | Keyword('Then') | Keyword('And')) + \
    restOfLine + \
    Optional(TABLE | MULTILINE)
STATEMENT.setParseAction(Statement)

"""
Background:
"""
BACKGROUND_DEFN = \
    Suppress(Keyword('Background') + ':' + EOL)
BACKGROUND_DEFN.setParseAction(Background)

BACKGROUND = Group(
    BACKGROUND_DEFN('node') +
    Group(ZeroOrMore(STATEMENT))('statements')
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
    Group(ZeroOrMore(STATEMENT))('statements') +
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
    Group(SkipTo(BACKGROUND))('description') +
    Optional(BACKGROUND('background')) +
    Group(OneOrMore(SCENARIO))('scenarios') +
    stringEnd)
FEATURE.setParseAction(Feature.add_blocks)


def from_string(cls, string):
    """
    Parse a Feature object from a string
    """

    tokens = FEATURE.parseString(string)
    return tokens[0]

Feature.from_string = classmethod(from_string)


if __name__ == '__main__':
    from pyparsing import ParseException
    try:
        feature = Feature.from_string('''
Feature: an example feature

    A short definition
    That is really not very interesting

    Background:
        Given something

    Scenario: this is a scenario
        Given something
        When I do something
        Then I can observe it

    Scenario Outline: this is a scenario outline
        Given step
        Then stop

        Examples:
            | farm   | town  |
            | possum | hippo |
''')
    except ParseException as e:
        print e

    assert feature.name == 'an example feature'

    try:
        feature = Feature.from_string('''
@badger
@stoat
Feature: an example feature

    Background:
        Given I have badgers in the database
        And I am a penguin
        And this step has a table
            | badger           | stoat |
            | smells like teen | stoat |
        And this step has a multiline string
        """
        Something in here
        """

    @tagged
    Scenario: empty

    Scenario: not empty
        Then success

    Scenario: has examples
        Examples:
            | badger | stoat |
            | 1      | 2     |
''')

        assert isinstance(feature, Feature)
        assert feature.name == 'an example feature'

        assert len(feature.background.statements) == 4

        scenarios = feature.scenarios
        assert len(scenarios) == 3
        assert [scenario.name for scenario in scenarios] == \
               ['empty', 'not empty', 'has examples']
        assert [len(scenario.statements) for scenario in scenarios] == \
               [0, 1, 0]

    except ParseException as e:
        print e.line
        print e
