"""
A Gherkin parser written using pyparsing
"""

from pyparsing import (Keyword,
                       lineStart,
                       lineEnd,
                       printables,
                       restOfLine,
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


class Block(object):
    """
    A generic block, e.g. Feature:, Scenario:

    Blocks contain type-specific child content as well as tags
    """
    def __init__(self, tokens):
        self.name = tokens[1]

    def __repr__(self):
        return '{klass}<{tag}>'.format(klass=self.__class__.__name__,
                                       tag=self.name)


class Feature(Block):
    pass


"""
@tag
"""
TAG = Suppress(lineStart + '@') + Word(printables) + Suppress(lineEnd)
TAG.setParseAction(Tag)

"""
Feature: description
"""
FEATURE_DEFN = lineStart + \
    Keyword('Feature') + Suppress(':') + \
    Suppress(White()) + \
    restOfLine
FEATURE_DEFN.setParseAction(Feature)

"""
Complete feature file definition
"""
FEATURE = \
    ZeroOrMore(TAG) + \
    FEATURE_DEFN


if __name__ == '__main__':
    print FEATURE.parseString('''
Feature: an example feature
''')

    tokens = FEATURE.parseString('''
@badger
@stoat
Feature: an example feature
''')
    for token in tokens:
        print token, type(token)
