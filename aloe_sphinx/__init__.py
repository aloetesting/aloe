"""
Extensions to Sphinx_ for documenting Aloe packages.

Add these extensions to your Sphinx_ ``conf.py``:

.. code-block:: python

    extensions = [
        'sphinx.ext.autodoc',
        'aloe_sphinx.gerkindomain',
        'aloe_sphinx.autosteps',
    ]

Gherkin Domain
~~~~~~~~~~~~~~

.. object:: aloe_sphinx.gherkindomain

.. automodule:: aloe_sphinx.gherkindomain

Steps Autodocumenter
~~~~~~~~~~~~~~~~~~~~

.. object:: aloe_sphinx.autosteps

.. automodule:: aloe_sphinx.autosteps

.. _Sphinx: http://sphinx-doc.org/
"""
