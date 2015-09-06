# -*- coding: utf-8 -*-
"""
A Gherkin parser written using pyparsing.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin,wildcard-import,unused-wildcard-import
from builtins import *
# pylint:enable=redefined-builtin,wildcard-import,unused-wildcard-import
from future import standard_library
standard_library.install_aliases()

import os
from collections import OrderedDict
from copy import copy
from io import StringIO

from gherkin3.dialect import Dialect
from gherkin3.parser import Parser
from gherkin3.token_matcher import TokenMatcher
from gherkin3.token_scanner import TokenScanner as BaseTokenScanner

from aloe import strings
from aloe.exceptions import LettuceSyntaxError
from aloe.utils import memoizedproperty

# Pylint can't figure out methods vs. properties and which classes are
# abstract
# pylint:disable=abstract-method


class TokenScanner(BaseTokenScanner):
    """Gherkin 3 token scanner that explicitly takes a string or a filename."""

    # pylint:disable=super-init-not-called
    def __init__(self, string=None, filename=None):
        if string:
            if filename:
                raise ValueError(
                    "Cannot provide string and filename together.")
            self.io = StringIO(string)  # pylint:disable=invalid-name
        elif filename:
            self.io = open(filename, 'r')
        else:
            raise ValueError("Must provide either string or filename.")

        self.line_number = 0
    # pylint:enable=super-init-not-called


class LanguageTokenMatcher(TokenMatcher):
    """Gherkin 3 token matcher that always uses the given language."""

    def __init__(self, dialect_name='en'):
        self.actual_dialect_name = dialect_name
        super().__init__(dialect_name=dialect_name)

    def _change_dialect(self, dialect_name, location=None):
        """Force the dialect name given in the constructor."""
        super()._change_dialect(self.actual_dialect_name, location=location)


def cell_values(row):
    """Extract cell values from a table header or row."""

    return tuple(cell['value'] for cell in row['cells'])


class Node(object):
    """
    A base parse node.
    """

    def __init__(self, parsed, filename=None):
        """Construct the node from Gherkin parse results."""
        self.line = parsed['location']['line']
        self.col = parsed['location']['column']
        self.filename = filename

    @property
    def feature(self):
        """The feature this node ultimately belongs to."""

        raise NotImplementedError

    @property
    def location(self):
        """Location as 'filename:line'"""

        return '{filename}:{line}'.format(
            filename=os.path.relpath(self.filename),
            line=self.line,
        )

    @property
    def text(self):
        """The text for this node."""

        raise NotImplementedError

    indent = 0  # The indent to use when printing the node

    def represented(self):
        """A representation of the node."""

        result = ' ' * self.indent + self.text.strip()

        return result


class Step(Node):
    """
    A single statement within a test.

    A :class:`Scenario` or :class:`Background` is composed of multiple
    :class:`Step`.
    """

    table = None
    """
    A Gherkin table as an iterable of rows, themselves iterables of cells.

    e.g.:

    .. code-block:: gherkin

        Then I have fruit:
            | apples | oranges |
            | 0      | 2       |

    Becomes:

    .. code-block:: python

        (('apples', 'oranges'), ('0', '2'))
    """

    multiline = None
    """
    A Gherkin multiline string with the appropriate indenting removed.

    .. code-block:: gherkin

        Then I have poem:
            \"\"\"
            Glittering-Minded deathless Aphrodite,
            I beg you, Zeus’s daughter, weaver of snares,
            Don’t shatter my heart with fierce
            Pain, goddess,
            \"\"\"
    """

    def __init__(self, parsed, background=None, scenario=None, **kwargs):
        super().__init__(parsed, **kwargs)

        if background:
            self.background = background
        elif scenario:
            self.scenario = scenario
        else:
            raise ValueError(
                "Step must belong to either a scenario or a background.")

        self.sentence = parsed['keyword'] + parsed['text']
        """The sentence parsed for this step."""

        try:
            argument_type = parsed['argument']['type']
        except KeyError:
            argument_type = None

        if argument_type == 'DataTable':
            self.table = tuple(
                cell_values(row)
                for row in parsed['argument']['rows']
            )

        elif argument_type == 'DocString':
            self.multiline = parsed['argument']['content']

    @property
    def text(self):
        return self.sentence

    def __str__(self):
        return '<Step: "%s">' % self.sentence

    def __repr__(self):
        return str(self)

    def parse_steps_from_string(self, string, **kwargs):
        """
        Parse a number of steps, returns an iterable of :class:`Step`.

        This is used by :func:`step.behave_as`.
        """

        try:
            container = self.scenario
            is_scenario = True
        except AttributeError:
            container = self.background
            is_scenario = False

        # Gherkin can't parse anything other than complete features
        feature_string = """
        # language: {feature.language}
        {feature.keyword}: feature

        {container.keyword}: scenario
        {string}
        """.format(
            feature=self.feature,
            container=container,
            string=string,
        )

        feature = self.feature.parse(string=feature_string,
                                     filename=self.filename)

        if is_scenario:
            return feature.scenarios[0].steps
        else:
            return feature.background.steps

    @property
    def feature(self):
        """
        The :class:`Feature` this step is a part of.
        """

        try:
            return self.scenario.feature
        except AttributeError:
            return self.background.feature

    @memoizedproperty
    def keys(self):
        """
        Return the first row of a table if this statement contains one.
        """
        if self.table:
            return tuple(self.table[0])
        else:
            return ()

    @memoizedproperty
    def hashes(self):
        """
        Return the table attached to the step as an iterable of hashes, where
        the first row - the column headings - supplies keys for all the others.

        e.g.:

        .. code-block:: gherkin

            Then I have fruit:
                | apples | oranges |
                | 0      | 2       |

        Becomes:

        .. code-block:: python

            ({
                'apples': '0',
                'oranges': '2',
            },)
        """

        if not self.table:
            return ()

        keys = self.keys

        return tuple(
            dict(zip(keys, row))
            for row in self.table[1:]
        )

    @memoizedproperty
    def max_length(self):
        """
        The max length of the feature, description and child blocks
        """

        return max(
            0,
            strings.get_terminal_width(self.represented(table=False,
                                                        multiline=False)),
            *[strings.get_terminal_width(line)
              for line in self.represent_table().splitlines()]
        )

    indent = 4

    # pylint:disable=arguments-differ
    def represented(self, table=True, multiline=True, color=str):
        """
        Render the line.
        """

        lines = [color(super().represented())]

        if table and self.table:
            lines.append(self.represent_table(cell_wrap=color))

        if multiline and self.multiline:
            lines.append(self.represent_multiline(string_wrap=color))

        return '\n'.join(lines)
    # pylint:enable=arguments-differ

    def represent_table(self, **kwargs):
        """
        Render the table.

        :param cell_wrap: color to use inside the table cells
        """

        return strings.represent_table(
            self.table, indent=self.indent + 2, **kwargs)

    def represent_multiline(self, string_wrap=str):
        """
        Render the multiline.

        :param string_wrap: color to use inside the string
        """

        indent = self.indent + 2

        lines = [' ' * indent + '"""']
        lines += [' ' * indent + string_wrap(line)
                  for line in self.multiline.splitlines()]
        lines += [' ' * indent + '"""']

        return '\n'.join(lines)

    def resolve_substitutions(self, outline):
        """
        Creates a copy of the step with any <variables> resolved.
        """

        replaced = copy(self)

        def replace_vars(string):
            """Replace all the variables in a string."""
            for key, value in outline.items():
                key = '<{key}>'.format(key=key)
                string = string.replace(key, value)
            return string

        replaced.sentence = replace_vars(self.sentence)

        if self.multiline:
            replaced.multiline = replace_vars(self.multiline)

        if self.table:
            replaced.table = tuple(
                tuple(
                    replace_vars(cell)
                    for cell in row
                )
                for row in self.table
            )

        return replaced

    def step_keyword(self, kind):
        """
        An appropriate keyword for a particular kind of step
        (Given, When, Then) for the language the current step is written in.
        """

        dialect = self.feature.dialect
        keywords = {
            'given': dialect.given_keywords,
            'when': dialect.when_keywords,
            'then': dialect.then_keywords,
        }[kind]()

        # Gherkin allows '*' as a keyword; skip it to be sure the keyword is
        # specifically for the given kind
        return next(
            keyword for keyword in keywords
            if not keyword.startswith('*')
        )


class StepContainer(Node):
    """A node containing steps, e.g. Feature:, Scenario:"""

    step_class = Step

    container_name = 'container'  # override in subclasses

    @property
    def feature(self):
        return self._feature

    def __init__(self, parsed, feature=None, filename=None, **kwargs):
        super().__init__(parsed, filename=filename, **kwargs)

        self._feature = feature

        # Put a reference to the parent node into all the steps
        parent_ref = {self.container_name: self}

        self.steps = tuple(
            self.step_class(step, filename=filename, **parent_ref)
            for step in parsed['steps']
        )

    indent = 2


class HeaderNode(Node):
    """
    Nodes with a header consisting of a keyword, name and a number of tags.
    """

    def __init__(self, parsed, **kwargs):
        super().__init__(parsed, **kwargs)

        self._tags = tuple(
            tag['name'][1:] for tag in parsed['tags']
        )
        self.keyword = parsed['keyword']
        self.name = parsed['name'].strip()

        if self.name == '':
            raise LettuceSyntaxError(
                None,
                "{line}:{col} {klass} must have a name".format(
                    line=self.line,
                    col=self.col,
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
        """
        Tags for a feature.

        Tags are applied to a feature using the appropriate Gherkin syntax:

        .. code-block:: gherkin

            @tag1 @tag2
            Feature: Eat leaves
        """
        return self._tags

    @property
    def text(self):
        """The text for this block."""

        return '{keyword}: {name}'.format(keyword=self.keyword,
                                          name=self.name)

    def represent_tags(self):
        """
        Render the tags of a tagged block.
        """

        return ' ' * self.indent + '  '.join('@%s' % tag for tag in self.tags)


class Background(StepContainer):
    """The background of all :class:`Scenario` in a :class:`Feature`."""
    container_name = 'background'

    text = 'Background:'


class Outline(OrderedDict, Node):
    """An outline within a :class:`Scenario`."""

    def __init__(self, keys, table_row, filename=None):
        """Construct the outline."""

        # Extract values
        OrderedDict.__init__(self, zip(keys, cell_values(table_row)))

        # Store the file and line information
        Node.__init__(self, table_row, filename=filename)


class Scenario(HeaderNode, StepContainer):
    """A scenario within a :class:`Feature`."""

    container_name = 'scenario'

    def __init__(self, parsed, **kwargs):
        super().__init__(parsed, **kwargs)

        # Build a list of outline hashes
        # A single scenario can have multiple example blocks, the returned
        # token is a list of table tokens
        self.outlines = ()

        for example_table in parsed.get('examples', ()):
            # the first row of the table is the column headings
            keys = cell_values(example_table['tableHeader'])

            self.outlines += tuple(
                Outline(keys, row)
                for row in example_table['tableBody']
            )

    indent = 2

    def represent_outlines(self):
        """
        Render the outlines table.
        """

        return strings.represent_table(
            self.outlines_table, indent=self.indent + 2)

    @memoizedproperty
    def max_length(self):
        """
        The max horizontal length of the feature, description and child blocks.
        """

        return max(
            0,
            strings.get_terminal_width(self.represented()),
            *([step.max_length for step in self.steps] +
              [strings.get_terminal_width(line)
               for line in self.represent_outlines().splitlines()])
        )

    @memoizedproperty
    def outlines_table(self):
        """
        Return the outlines as a table.
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
        """Tags for the :attr:`feature` and the scenario."""
        return self._tags + self.feature.tags

    @property
    def evaluated(self):
        """
        Yield the outline and steps.
        """

        for outline in self.outlines:
            steps = [step.resolve_substitutions(outline)
                     for step in self.steps]

            # set a backref to the scenario
            for step in steps:
                step.scenario = self

            yield (outline, steps)


class Description(Node):
    """
    The description block of a feature.
    """

    def __init__(self, parsed, **kwargs):
        super().__init__(parsed, **kwargs)

        description = parsed.get('description', '')
        self.lines = tuple(line.strip() for line in description.split('\n'))

    def __str__(self):
        return '\n'.join(self.lines)

    def __repr__(self):
        return str(self)

    indent = 2

    def represented(self):
        return '\n'.join(
            self.represent_line(n)
            for n, _ in enumerate(self.lines)
        )

    def represent_line(self, idx):
        """
        Render the nth line in the description.
        """

        line = self.lines[idx]
        result = ' ' * self.indent + line

        return result

    @memoizedproperty
    def description_at(self):
        """
        Return a tuple of lines in the string containing the description.
        """

        offset = self.line

        return tuple(offset + lineno for lineno, _
                     in enumerate(self.lines))

    @memoizedproperty
    def max_length(self):
        """
        The maximum length of all description lines.
        """
        try:
            return max(
                strings.get_terminal_width(self.represent_line(n))
                for n, _ in enumerate(self.lines)
            )
        except ValueError:
            return 0


class Feature(HeaderNode):
    """
    A complete Gherkin feature.

    Features can either be constructed :func:`from_file` or
    :func:`from_string`.
    """

    background_class = Background
    scenario_class = Scenario

    background = None

    def __init__(self, parsed, filename=None, **kwargs):
        super().__init__(parsed, filename=filename, **kwargs)

        self.language = parsed['language']

        self.description_node = Description(parsed, filename=filename)

        if 'background' in parsed:
            self.background = self.background_class(parsed['background'],
                                                    filename=filename,
                                                    feature=self)

        self.scenarios = tuple(
            self.scenario_class(scenario, filename=filename, feature=self)
            for scenario in parsed['scenarioDefinitions']
        )

    @classmethod
    def parse(cls, string=None, filename=None, language=None):
        """
        Parse either a string or a file.
        """

        parser = Parser()
        if language:
            if language == 'pt-br':
                language = 'pt'
            token_matcher = LanguageTokenMatcher(language)
        else:
            token_matcher = TokenMatcher()

        if string:
            token_scanner = TokenScanner(string=string)
        else:
            token_scanner = TokenScanner(filename=filename)

        return cls(
            parser.parse(token_scanner, token_matcher=token_matcher),
            filename=filename,
        )

    @classmethod
    def from_string(cls, string, language=None):
        """
        Parse a string into a :class:`Feature`.
        """

        return cls.parse(string=string, language=language)

    @classmethod
    def from_file(cls, filename, language=None):
        """
        Parse a file or filename into a :class:`Feature`.
        """

        return cls.parse(filename=filename, language=language)

    @property
    def description(self):
        """
        The description of the feature (the text that comes directly under
        the feature).
        """
        return str(self.description_node)

    @property
    def dialect(self):
        """
        The Gherkin dialect for the feature.
        """

        return Dialect.for_name(self.language)

    @property
    def feature(self):
        """
        Convenience property for generic functions.
        """

        return self

    @memoizedproperty
    def max_length(self):
        """
        The max horizontal length of the feature, description and child blocks.

        This is used for aligning rendered output.
        """

        return max(
            0,
            strings.get_terminal_width(
                self.represented(description=False)),
            self.description_node.max_length,
            *[scenario.max_length for scenario in self.scenarios]
        )

    # pylint:disable=arguments-differ
    def represented(self, description=True):
        result = super().represented()

        if description and self.description != '':
            result += '\n'
            result += self.description_node.represented()

        return result
