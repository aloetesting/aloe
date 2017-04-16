============================
 Aloe: BDD testing via nose
============================

Aloe is a Gherkin_-based Behavior Driven Development tool for Python based
on Nose_.

Aloe makes your feature files and steps an intuiative part of the traceback:

.. code-block:: pytb
    :emphasize-lines: 4,5

    Traceback (most recent call last):
      File ".../python_env/lib/python2.7/site-packages/aloe/registry.py", line 161, in wrapped
        return function(*args, **kwargs)
      File ".../app/features/user_registration.feature", line 325, in Unlock renewal pages
        And I should see the clickable link to the renewal page
      File ".../python_env/lib/python2.7/site-packages/aloe/registry.py", line 161, in wrapped
        return function(*args, **kwargs)
      File ".../features/steps/__init__.py", line 280, in should_see_renewal_page
        assert_true(contains_content(world.browser, text))
    AssertionError: False is not true

.. toctree::
    :maxdepth: 2

    aloe
    features
    steps
    hooks
    classes
    extras
    extending
    porting

.. include:: getting-started.rst


History
=======

`Aloe` originally started life as a branch of the Python BDD tool Lettuce_.
Like so many succulents, it grew into so much more than that.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. include:: links.rst
