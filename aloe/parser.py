# -*- coding: utf-8 -*-
"""
A Gherkin parser written using pyparsing.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin
from builtins import *
# pylint:enable=redefined-builtin
from future import standard_library
standard_library.install_aliases()

import os
from collections import OrderedDict
from copy import deepcopy
from warnings import warn

from gherkin3.parser import Parser
from gherkin3.token_matcher import TokenMatcher
from gherkin3.token_scanner import TokenScanner

from aloe import strings
from aloe.exceptions import LettuceSyntaxError, LettuceSyntaxWarning
from aloe.utils import memoizedproperty


def cell_values(row):
    """Extract cell values from a table header or row."""

    return tuple(cell['value'] for cell in row['cells'])


class LanguageTokenMatcher(TokenMatcher):
    """A token matcher that actually remembers the language it's set to."""

    def __init__(self, dialect_name='en'):
        self.actual_dialect_name = dialect_name
        super().__init__(dialect_name=dialect_name)

    def _change_dialect(self, dialect_name, location=None):
        """Force the dialect name given in the constructor."""
        super()._change_dialect(self.actual_dialect_name, location=location)


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
    def text(self):
        """The text for this node."""

        raise NotImplementedError

    def represented(self, indent=0, annotate=True):
        """A representation of the node."""

        s = ' ' * indent + self.text.strip()

        if annotate:
            s = strings.ljust(s, self.feature.max_length + 1) + \
                '# {filename}:{line}'.format(
                    filename=os.path.relpath(self.filename),
                    line=self.line,
                )

        return s


class Step(Node):
    """
    A single statement within a test.

    A :class:`Scenario` or :class:`Background` is composed of multiple
    :class:`Step`.
    """

    table = None
    """
    A Gherkin table as a list of lists.

    e.g.:

    .. code-block:: gherkin

        Then I have fruit:
            | apples | oranges |
            | 0      | 2       |

    Becomes:

    .. code-block:: python

        [['apples', 'oranges', '0', '2']]
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
        if scenario:
            self.scenario = scenario

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
        Parse a number of steps, returns a list of :class:`Step`.

        This is used by :func:`step.behave_as`.
        """

        # TODO: Gherkin can't parse anything other than complete features
        # TODO: This won't work with non-default languages
        feature_string = """
        Feature: feature

        Scenario: scenario
        """ + string

        feature = self.feature.from_string(feature_string,
                                           filename=self.filename)
        return feature.scenarios[0].steps

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
        Return the table attached to the step as a list of hashes, where the
        first row is the column headings.

        e.g.:

        .. code-block:: gherkin

            Then I have fruit:
                | apples | oranges |
                | 0      | 2       |

        Becomes:

        .. code-block:: python

            [{
                'apples': '0',
                'oranges': '2',
            }]
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
            strings.get_terminal_width(self.represented(annotate=False,
                                                        table=False,
                                                        multiline=False)),
            *[strings.get_terminal_width(line)
              for line in self.represent_table().splitlines()]
        )

    # pylint:disable=too-many-arguments,arguments-differ
    def represented(self, indent=4, annotate=True,
                    table=True, multiline=True,
                    color=str):
        """
        Render the line.
        """

        lines = [color(super().represented(indent=indent, annotate=annotate))]

        if table and self.table:
            lines.append(self.represent_table(indent=indent + 2,
                                              cell_wrap=color))

        if multiline and self.multiline:
            lines.append(self.represent_multiline(indent=indent + 2,
                                                  string_wrap=color))

        return '\n'.join(lines)
    # pylint:enable=too-many-arguments,arguments-differ

    def represent_table(self, indent=6, **kwargs):
        """
        Render the table.

        :param cell_wrap: color to use inside the table cells
        """

        return strings.represent_table(self.table, indent=indent, **kwargs)

    def represent_multiline(self, indent=6, string_wrap=str):
        """
        Render the multiline.

        :param string_wrap: color to use inside the string
        """

        lines = [' ' * indent + '"""']
        lines += [' ' * indent + string_wrap(line)
                  for line in self.multiline.splitlines()]
        lines += [' ' * indent + '"""']

        return '\n'.join(lines)

    def resolve_substitutions(self, outline):
        """
        Creates a copy of the step with any <variables> resolved.
        """

        replaced = deepcopy(self)

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


class StepContainer(Node):
    """A node containing steps, e.g. Feature:, Scenario:"""

    step_class = Step

    container_name = 'container'  # override in subclasses

    def __init__(self, parsed, feature=None, filename=None, **kwargs):
        super().__init__(parsed, filename=filename, **kwargs)

        self.feature = feature

        # Put a reference to the parent node into all the steps
        parent_ref = {self.container_name: self}

        self.steps = tuple(
            self.step_class(step, filename=filename, **parent_ref)
            for step in parsed['steps']
        )

    def represented(self, indent=2, annotate=True):
        """
        Include block indents.
        """

        return super().represented(indent=indent, annotate=annotate)


class Tagged(Node):
    """
    Tagged blocks contain type-specific child content as well as tags.
    """

    def __init__(self, parsed, **kwargs):
        super().__init__(parsed, **kwargs)

        self._tags = tuple(
            tag['name'][1:] for tag in parsed['tags']
        )
        # TODO: Why is this here?
        self.keyword = parsed['keyword']
        # TODO: And this
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

    def represent_tags(self, indent=0):
        """
        Render the tags of a tagged block.
        """

        return ' ' * indent + '  '.join('@%s' % tag for tag in self.tags)


class Background(StepContainer):
    """The background of all :class:`Scenario` in a :class:`Feature`."""
    container_name = 'background'

    text = 'Background:'


class Scenario(Tagged, StepContainer):
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

            # TODO: store line information here
            self.outlines += tuple(
                OrderedDict(zip(keys, cell_values(row)))
                for row in example_table['tableBody']
            )

    def represented(self, indent=2, **kwargs):
        return super().represented(indent=indent, **kwargs)

    def represent_outlines(self, indent=4):
        """
        Render the outlines table.
        """

        return strings.represent_table(self.outlines_table, indent=indent)

    @memoizedproperty
    def max_length(self):
        """
        The max horizontal length of the feature, description and child blocks.
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

        # TODO: Should be None
        description = parsed.get('description', '')
        self.lines = tuple(line.strip() for line in description.split('\n'))

    def __str__(self):
        return '\n'.join(self.lines)

    def __repr__(self):
        return str(self)

    def represented(self, indent=2, annotate=True):
        return '\n'.join(
            self.represent_line(n, annotate=annotate)
            for n, _ in enumerate(self.lines)
        )

    def represent_line(self, n, indent=2, annotate=True):
        """
        Render the nth line in the description.
        """

        line = self.lines[n]
        s = ' ' * indent + line

        if annotate:
            s = strings.ljust(s, self.feature.max_length + 1) + \
                '# {file}:{line}'.format(
                    file=self.filename,
                    line=self.description_at[n])

        return s

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
                strings.get_terminal_width(
                    self.represent_line(n, annotate=False))
                for n, _ in enumerate(self.lines)
            )
        except ValueError:
            return 0


class Feature(Tagged):
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
    def from_string(cls, string, filename=None, language=None):
        """
        Parse a string into a :class:`Feature`.
        """

        # TODO: Memoize some of this
        parser = Parser()
        if language:
            if language == 'pt-br':
                language = 'pt'
            token_matcher = LanguageTokenMatcher(language)
        else:
            token_matcher = TokenMatcher()
        return cls(
            parser.parse(TokenScanner(string), token_matcher=token_matcher),
            filename=filename,
        )

    @classmethod
    def from_file(cls, filename, language=None):
        """
        Parse a file or filename into a :class:`Feature`.
        """

        # FIXME: Don't rely on gherkin's "filename as string" feature
        return cls.from_string(filename, filename=filename, language=language)

    @property
    def description(self):
        """
        The description of the feature (the text that comes directly under
        the feature).
        """
        return str(self.description_node)

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
                self.represented(annotate=False, description=False)),
            self.description_node.max_length,
            *[scenario.max_length for scenario in self.scenarios]
        )

    # pylint:disable=arguments-differ
    def represented(self, indent=0, annotate=True, description=True):
        s = super().represented(indent=indent, annotate=annotate)

        # FIXME: indent here is description default indent + feature
        # requested indent
        if description and self.description != '':
            s += '\n'
            s += self.description_node.represented(annotate=annotate)

        return s
