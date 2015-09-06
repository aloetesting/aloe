# -*- coding: utf-8 -*-
"""
Test French language parsing.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from nose.tools import assert_equal
from aloe.parser import Feature

SCENARIO = u"""
Scénario: Ajout de plusieurs cursus dans la base de mon université
    Soit Une liste de cursus disponibles dans mon université
        | Nom                       | Durée    |
        | Science de l'Informatique | 5 ans    |
        | Nutrition                 | 4 ans    |
    Quand je consolide la base dans 'cursus.txt'
    Alors je vois que la 1er ligne de 'cursus.txt' contient 'Science de l'Informatique:5
    Et je vois que la 2em ligne de 'cursus.txt' contient 'Nutrition:4'
"""  # noqa

OUTLINED_SCENARIO = u"""
Plan du Scénario: Ajouter 2 nombres
    Soit <input_1> entré dans la calculatrice
    Et <input_2> entré dans la calculatrice
    Quand je presse <bouton>
    Alors je doit avoir <output> à l'écran

    Exemples:
      | input_1 | input_2 | bouton | output |
      | 20      | 30      | add    | 50     |
      | 2       | 5       | add    | 7      |
      | 0       | 40      | add    | 40     |
"""

OUTLINED_SCENARIO2 = u"""
Plan du Scénario: Ajouter 2 nombres
    Soit <input_1> entré dans la calculatrice
    Et <input_2> entré dans la calculatrice
    Quand je presse <bouton>
    Alors je doit avoir <output> à l'écran

    Exemples:
      | input_1 | input_2 | bouton | output |
      | 20      | 30      | add    | 50     |
      | 2       | 5       | add    | 7      |
      | 0       | 40      | add    | 40     |
"""
OUTLINED_SCENARIO3 = u"""
Plan du Scénario: Ajouter 2 nombres
    Soit <input_1> entré dans la calculatrice
    Et <input_2> entré dans la calculatrice
    Quand je presse <bouton>
    Alors je doit avoir <output> à l'écran

    Exemples:
      | input_1 | input_2 | bouton | output |
      | 20      | 30      | add    | 50     |
      | 2       | 5       | add    | 7      |
      | 0       | 40      | add    | 40     |
"""

OUTLINED_FEATURE = u"""
Fonctionnalité: Faire plusieur choses en même temps
    De façon à automatiser les tests
    En tant que fainéant
    J'utilise les plans de scénario

    Plan du Scénario: Ajouter 2 nombres
        Soit <input_1> entré dans la calculatrice
        Et <input_2> entré dans la calculatrice
        Quand je presse <bouton>
        Alors je doit avoir <output> à l'écran

    Exemples:
        | input_1 | input_2 | bouton | output |
        | 20      | 30      | add    | 50     |
        | 2       | 5       | add    | 7      |
        | 0       | 40      | add    | 40     |
"""
OUTLINED_FEATURE2 = u"""
Fonctionnalité: Faire plusieur choses en même temps
    De façon à automatiser les tests
    En tant que fainéant
    J'utilise les plans de scénario

    Plan du Scénario: Ajouter 2 nombres
        Soit <input_1> entré dans la calculatrice
        Et <input_2> entré dans la calculatrice
        Quand je presse <bouton>
        Alors je doit avoir <output> à l'écran

    Exemples:
        | input_1 | input_2 | bouton | output |
        | 20      | 30      | add    | 50     |
        | 2       | 5       | add    | 7      |
        | 0       | 40      | add    | 40     |
"""


def parse_scenario(string, language=None):
    """Parse a scenario, prefixing it with a feature header."""
    feature = u"""
    Fonctionnalité: parse_scenario
    """

    feature += string
    feature = Feature.from_string(feature, language=language)

    return feature.scenarios[0]


def test_scenario_fr_from_string():
    """
    Language: FR -> Scenario.from_string
    """

    scenario = parse_scenario(SCENARIO, language='fr')

    assert_equal(
        scenario.name,
        u'Ajout de plusieurs cursus dans la base de mon université'
    )
    assert_equal(
        scenario.steps[0].hashes,
        (
            {'Nom': u"Science de l'Informatique", u'Durée': '5 ans'},
            {'Nom': u'Nutrition', u'Durée': '4 ans'},
        )
    )


def test_scenario_outline1_fr_from_string():
    """
    Language: FR -> Scenario.from_string, with scenario outline, first case
    """

    scenario = parse_scenario(OUTLINED_SCENARIO, language='fr')

    assert_equal(
        scenario.name,
        'Ajouter 2 nombres'
    )
    assert_equal(
        scenario.outlines,
        (
            {u'input_1': u'20', u'input_2': u'30',
             u'bouton': u'add', u'output': u'50'},
            {u'input_1': u'2', u'input_2': u'5',
             u'bouton': u'add', u'output': u'7'},
            {u'input_1': u'0', u'input_2': u'40',
             u'bouton': u'add', u'output': u'40'},
        )
    )


def test_scenario_outline2_fr_from_string():
    """
    Language: FR -> Scenario.from_string, with scenario outline, second case
    """

    scenario = parse_scenario(OUTLINED_SCENARIO2, language='fr')

    assert_equal(
        scenario.name,
        'Ajouter 2 nombres'
    )
    assert_equal(
        scenario.outlines,
        (
            {u'input_1': u'20', u'input_2': u'30',
             u'bouton': u'add', u'output': u'50'},
            {u'input_1': u'2', u'input_2': u'5',
             u'bouton': u'add', u'output': u'7'},
            {u'input_1': u'0', u'input_2': u'40',
             u'bouton': u'add', u'output': u'40'},
        )
    )


def test_scenario_outline3_fr_from_string():
    """
    Language: FR -> Scenario.from_string, with scenario outline, third case
    """

    scenario = parse_scenario(OUTLINED_SCENARIO2, language='fr')

    assert_equal(
        scenario.name,
        'Ajouter 2 nombres'
    )
    assert_equal(
        scenario.outlines,
        (
            {u'input_1': u'20', u'input_2': u'30',
             u'bouton': u'add', u'output': u'50'},
            {u'input_1': u'2', u'input_2': u'5',
             u'bouton': u'add', u'output': u'7'},
            {u'input_1': u'0', u'input_2': u'40',
             u'bouton': u'add', u'output': u'40'},
        )
    )


def test_feature_fr_from_string():
    """
    Language: FR -> Feature.from_string
    """

    feature = Feature.from_string(OUTLINED_FEATURE, language='fr')

    assert_equal(
        feature.name,
        u'Faire plusieur choses en même temps'
    )

    assert_equal(
        feature.description,
        u"De façon à automatiser les tests\n"
        u"En tant que fainéant\n"
        u"J'utilise les plans de scénario"
    )

    (scenario, ) = feature.scenarios

    assert_equal(
        scenario.name,
        'Ajouter 2 nombres'
    )

    assert_equal(
        scenario.outlines,
        (
            {u'input_1': u'20', u'input_2': u'30',
             u'bouton': u'add', u'output': u'50'},
            {u'input_1': u'2', u'input_2': u'5',
             u'bouton': u'add', u'output': u'7'},
            {u'input_1': u'0', u'input_2': u'40',
             u'bouton': u'add', u'output': u'40'},
        )
    )


def test_feature_fr_from_string2():
    """
    Language: FR -> Feature.from_string, alternate name
    """

    feature = Feature.from_string(OUTLINED_FEATURE2, language='fr')

    assert_equal(
        feature.name,
        u'Faire plusieur choses en même temps'
    )

    assert_equal(
        feature.description,
        u"De façon à automatiser les tests\n"
        u"En tant que fainéant\n"
        u"J'utilise les plans de scénario"
    )

    (scenario, ) = feature.scenarios

    assert_equal(
        scenario.name,
        'Ajouter 2 nombres'
    )

    assert_equal(
        scenario.outlines,
        (
            {u'input_1': u'20', u'input_2': u'30',
             u'bouton': u'add', u'output': u'50'},
            {u'input_1': u'2', u'input_2': u'5',
             u'bouton': u'add', u'output': u'7'},
            {u'input_1': u'0', u'input_2': u'40',
             u'bouton': u'add', u'output': u'40'},
        )
    )
