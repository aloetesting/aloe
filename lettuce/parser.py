"""
A Gherkin parser written using pyparsing
"""

from pyparsing import (Keyword,
                       lineStart,
                       lineEnd,
                       Optional,
                       printables,
                       restOfLine,
                       stringEnd,
                       Suppress,
                       unicodeString,
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
        self.statement = ' '.join(tokens)

    def __repr__(self):
        return 'Statement<%s>' % self.statement


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

        self = tokens.pop(0)

        assert isinstance(self, cls)
        assert all(isinstance(token, Statement) for token in tokens)

        self.statements = tokens

        return self


class TaggedBlock(object):
    """
    Tagged blocks contain type-specific child content as well as tags
    """
    def __init__(self, tokens):
        self.tags = tokens[:-1]
        self.name = tokens[-1]

        assert all(isinstance(tag, Tag) for tag in self.tags)

    def __repr__(self):
        return '{klass}<{tag}>'.format(
            klass=self.__class__.__name__,
            tag=','.join([self.name] +
                         [' @%s' % tag.tag for tag in self.tags]))


class Background(Block):
    pass


class Feature(TaggedBlock):
    pass


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
Statement
"""
STATEMENT = \
    (Keyword('Given') | Keyword('When') | Keyword('Then') | Keyword('And')) + \
    restOfLine
STATEMENT.setParseAction(Statement)

"""
Background:
"""
BACKGROUND_DEFN = \
    Suppress(Keyword('Background') + ':' + EOL)
BACKGROUND_DEFN.setParseAction(Background)

BACKGROUND = \
    BACKGROUND_DEFN + \
    ZeroOrMore(STATEMENT)
BACKGROUND.setParseAction(Background.add_statements)

"""
Feature: description
"""
FEATURE_DEFN = \
    ZeroOrMore(TAG) + \
    Suppress(Keyword('Feature') + ':' + White()) + \
    restOfLine
FEATURE_DEFN.setParseAction(Feature)

DESCRIPTION = restOfLine

"""
Complete feature file definition
"""
FEATURE = \
    FEATURE_DEFN + \
    Optional(BACKGROUND) + \
    stringEnd


if __name__ == '__main__':
    from pyparsing import ParseException
    try:
        print FEATURE.parseString('''
Feature: an example feature

    A short definition
    That is really not very interesting

    Background:
        Given something
''')
    except ParseException as e:
        print e

    tokens = FEATURE.parseString('''
@badger
@stoat
Feature: an example feature

    Background:
        Given I have badgers in the database
        And I am a penguin
''')
    print
    for token in tokens:
        print token
