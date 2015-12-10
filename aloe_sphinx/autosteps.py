"""
An autodocumenter for Aloe steps built on top of :class:`sphinx.ext.autodoc`.

This extension will identify functions decorated with :func:`step` (including
private functions) and expose them in your documentation with their step
sentence.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin, unused-wildcard-import, wildcard-import
from builtins import *
# pylint:enable=redefined-builtin, unused-wildcard-import, wildcard-import

from types import FunctionType

from sphinx.ext.autodoc import FunctionDocumenter, ModuleDocumenter
from sphinx.util.inspect import safe_getmembers


def is_step(member):
    """Return true if the member is an Aloe step declaration"""
    return isinstance(member, FunctionType) and hasattr(member, 'sentence')


class StepsDocumenter(ModuleDocumenter):
    """Autodocumenter for Aloe step declarations"""

    def get_object_members(self, want_all):
        """
        Override the module introspection to add any steps not
        contained in __all__ into the member list.
        """

        ret, memberlist = super().get_object_members(want_all)

        for name, member in safe_getmembers(self.object):
            if is_step(member):
                if (name, member) in memberlist:
                    continue

                memberlist.append((name, member))

        return ret, memberlist

    def filter_members(self, members, want_all):
        """Override the filtering to prevent removing private steps."""

        members_copy = list(members)
        members = super().filter_members(members, want_all)

        for (name, member) in members_copy:
            if is_step(member):
                if (name, member, False) in members:
                    continue

                members.append((name, member, False))

        return members


class StepDocumenter(FunctionDocumenter):
    """Autodocumenter for steps"""

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return is_step(member) or \
            super().can_document_member(member, membername, isattr, parent)

    def add_directive_header(self, sig):
        directive = 'gherkin:restep'

        if is_step(self.object):
            name = self.object.sentence
            sourcename = self.get_sourcename()

            self.add_line(u'.. %s:: %s' % (directive, name),
                          sourcename)
            if self.options.noindex:
                self.add_line(u'   :noindex:', sourcename)
        else:
            return super().add_directive_header(sig)


def setup(app):
    """Initialize the extension."""
    app.add_autodocumenter(StepsDocumenter)
    app.add_autodocumenter(StepDocumenter)

    return {'version': '0.1', 'parallel_read_safe': False}
