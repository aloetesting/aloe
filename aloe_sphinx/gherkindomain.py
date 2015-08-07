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
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import
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
        signode += addnodes.desc_annotation(self.type_ + ' ', self.type_ + ' ')
        signode += nodes.strong(sig, sig)

        return sig


class GherkinDomain(Domain):
    """Domain for Gherkin syntax"""

    name = 'gherkin'
    label = 'Gherkin'

    directives = {
        'restep': GherkinREStep,
    }

    def merge_domaindata(self, docnames, otherdata):
        raise NotImplementedError("FIXME")

    # pylint:disable=too-many-arguments
    def resolve_any_xref(self, env, fromdocname, builder, target,
                         node, contnode):
        """FIXME: implement"""
        return []
    # pylint:enable=too-many-arguments


def setup(app):
    """Initialize extension"""
    app.add_domain(GherkinDomain)
