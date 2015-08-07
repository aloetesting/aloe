"""
The Gherkin Domain for Sphinx_ provides additional directives for
documenting steps using Sphinx.

.. rst:directive:: .. gherkin:restep:: Sentence regex

    Provide the documentation for a Gherkin regular expression step.

    For example:

    .. code-block:: rst

        .. gherkin:restep:: (?:Given|When|And) I visit the supermarket

            I am at the supermarket.

    Is rendered as:

        .. gherkin:restep:: (?:Given|When|And) I visit the supermarket

            I am at the supermarket.

.. _Sphinx: http://sphinx-doc.org/
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

from sphinx.directives import ObjectDescription
from sphinx.domains import Domain
from sphinx import addnodes
from docutils import nodes


class GherkinREStep(ObjectDescription):
    """Description of a Gherkin Regex Step"""

    type_ = 'Step'

    def handle_signature(self, sig, signode):
        signode += addnodes.desc_name(self.type_, self.type_)
        signode += nodes.inline(' ', ' ')
        signode += nodes.emphasis(sig, sig)

        return sig


class GherkinDomain(Domain):
    """Domain for Gherkin syntax"""

    name = 'gherkin'
    label = 'Gherkin'

    directives = {
        'restep': GherkinREStep,
    }


def setup(app):
    app.add_domain(GherkinDomain)
