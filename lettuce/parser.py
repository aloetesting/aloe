"""
A Gherkin parser written using pyparsing
"""

from pyparsing import (Keyword,
                       lineStart,
                       lineEnd,
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


class Block(object):
    """
    A generic block, e.g. Feature:, Scenario:

    Blocks contain type-specific child content as well as tags
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
    ZeroOrMore(TAG) + \
    Suppress(Keyword('Feature') + ':' + White()) + \
    restOfLine
FEATURE_DEFN.setParseAction(Feature)

"""
Complete feature file definition
"""
FEATURE = \
    FEATURE_DEFN + \
    stringEnd


if __name__ == '__main__':
    print FEATURE.parseString('''
Feature: an example feature

    A short definition
    That is really not very interesting
''')

    tokens = FEATURE.parseString('''
@badger
@stoat
Feature: an example feature
''')
    print
    for token in tokens:
        print token
