# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from os.path import dirname, abspath, join
from tests.asserts import capture_output, assert_equals

from lettuce import Runner

current_dir = abspath(dirname(__file__))
join_path = lambda *x: join(current_dir, *x)


def test_output_with_success_colorless():
    """Language: pt-br -> success colorless"""

    with capture_output() as (out, err):
        runner = Runner(join_path('pt-br', 'success', 'dumb.feature'),
                        verbosity=3)
        runner.run()

    assert_equals(out.getvalue(),
        u"\n"
        u"Funcionalidade: feature burra       # tests/functional/language_specific_features/pt-br/success/dumb.feature:3\n"
        u"  Como um programador               # tests/functional/language_specific_features/pt-br/success/dumb.feature:4\n"
        u"  Eu quero que este teste passe     # tests/functional/language_specific_features/pt-br/success/dumb.feature:5\n"
        u"  Para testar um cenário de sucesso # tests/functional/language_specific_features/pt-br/success/dumb.feature:6\n"
        u"\n"
        u"  #1\n"
        u"  Cenario: Fazer nada               # tests/functional/language_specific_features/pt-br/success/dumb.feature:8\n"
        u"    Dado que eu faço nada           # tests/functional/language_specific_features/pt-br/success/dumb_steps.py:6\n"
        u"\n"
        u"  ----------------------------------------------------------------------------\n"
        u"\n"
        u"1 feature (1 passed)\n"
        u"1 scenario (1 passed)\n"
        u"1 step (1 passed)\n"
    )


def test_output_of_table_with_success_colorless():
    """Language: pt-br -> success table colorless"""

    with capture_output() as (out, err):
        runner = Runner(join_path('pt-br', 'success', 'table.feature'),
                        verbosity=3)
        runner.run()

    assert_equals(out.getvalue(),
        u"\n"
        u"Funcionalidade: feature burra, com tabela      # tests/functional/language_specific_features/pt-br/success/table.feature:3\n"
        u"  Como um programador                          # tests/functional/language_specific_features/pt-br/success/table.feature:4\n"
        u"  Eu quero testar steps com tabelas            # tests/functional/language_specific_features/pt-br/success/table.feature:5\n"
        u"  Para ver o output em pt-br                   # tests/functional/language_specific_features/pt-br/success/table.feature:6\n"
        u"\n"
        u"  #1\n"
        u"  Cenario: Fazer nada, com tabelas :)          # tests/functional/language_specific_features/pt-br/success/table.feature:8\n"
        u"    Dado que eu brinco com os seguintes itens: # tests/functional/language_specific_features/pt-br/success/table_steps.py:6\n"
        u"      | id | description  |\n"
        u"      | 12 | some desc    |\n"
        u"      | 64 | another desc |\n"
        u"\n"
        u"  ----------------------------------------------------------------------------\n"
        u"\n"
        u"1 feature (1 passed)\n"
        u"1 scenario (1 passed)\n"
        u"1 step (1 passed)\n"
    )


def test_output_outlines_success_colorless():
    """Language: pt-br -> success outlines colorless"""

    with capture_output() as (out, err):
        runner = Runner(join_path('pt-br', 'success', 'outlines.feature'),
                        verbosity=3)
        runner.run()

    assert_equals(out.getvalue(),
        u'\n'
        u'Funcionalidade: outlines em português                                  # tests/functional/language_specific_features/pt-br/success/outlines.feature:3\n'
        u'  Como um programador                                                  # tests/functional/language_specific_features/pt-br/success/outlines.feature:4\n'
        u'  Eu quero testar cenários esquemáticos                                # tests/functional/language_specific_features/pt-br/success/outlines.feature:5\n'
        u'  Para ver o output em pt-br                                           # tests/functional/language_specific_features/pt-br/success/outlines.feature:6\n'
        u'\n'
        u'  #1\n'
        u'  Esquema do Cenário: Fazer nada, repetidas vezes, através de esquemas # tests/functional/language_specific_features/pt-br/success/outlines.feature:8\n'
        u'\n'
        u'  Example #1:\n'
        u'    | dado1 | isso  | aquilo    |\n'
        u'    | algo  | assim | funcional |\n'
        u'\n'
        u'    Dado que tenho o <dado1>                                           # tests/functional/language_specific_features/pt-br/success/outlines_steps.py:13\n'
        u'    Quando eu faço algo com <isso>                                     # tests/functional/language_specific_features/pt-br/success/outlines_steps.py:22\n'
        u'    Então eu fico feliz em ver <aquilo>                                # tests/functional/language_specific_features/pt-br/success/outlines_steps.py:31\n'
        u'\n'
        u"  ----------------------------------------------------------------------------\n"
        u'\n'
        u'  Example #2:\n'
        u'    | dado1 | isso | aquilo |\n'
        u'    | outro | aqui | também |\n'
        u'\n'
        u'    Dado que tenho o <dado1>                                           # tests/functional/language_specific_features/pt-br/success/outlines_steps.py:13\n'
        u'    Quando eu faço algo com <isso>                                     # tests/functional/language_specific_features/pt-br/success/outlines_steps.py:22\n'
        u'    Então eu fico feliz em ver <aquilo>                                # tests/functional/language_specific_features/pt-br/success/outlines_steps.py:31\n'
        u'\n'
        u"  ----------------------------------------------------------------------------\n"
        u'\n'
        u'  Example #3:\n'
        u'    | dado1 | isso        | aquilo        |\n'
        u'    | dados | funcionarão | com unicode ! |\n'
        u'\n'
        u'    Dado que tenho o <dado1>                                           # tests/functional/language_specific_features/pt-br/success/outlines_steps.py:13\n'
        u'    Quando eu faço algo com <isso>                                     # tests/functional/language_specific_features/pt-br/success/outlines_steps.py:22\n'
        u'    Então eu fico feliz em ver <aquilo>                                # tests/functional/language_specific_features/pt-br/success/outlines_steps.py:31\n'
        u'\n'
        u"  ----------------------------------------------------------------------------\n"
        u'\n'
        u'1 feature (1 passed)\n'
        u'3 scenarios (3 passed)\n'
        u'9 steps (9 passed)\n'
    )
