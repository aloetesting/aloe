# -*- coding: utf-8 -*-
# Aloe - Cucumber runner for Python based on Lettuce and Nose
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

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import str
from future import standard_library
standard_library.install_aliases()

from nose.tools import assert_equals

from aloe.languages import Language
from aloe.parser import Feature

SCENARIO = u"""
Cenário: Consolidar o banco de dados de cursos universitários em arquivo texto
    Dados os seguintes cursos cadastrados no banco de dados da universidade:
       | Nome                    | Duração  |
       | Ciência da Computação   | 5 anos   |
       | Nutrição                | 4 anos   |
    Quando eu consolido os dados no arquivo 'cursos.txt'
    Então a 1a linha do arquivo 'cursos.txt' contém 'Ciência da Computação:5'
    E a 2a linha do arquivo 'cursos.txt' contém 'Nutrição:4'
"""

SCENARIO_OUTLINE1 = u'''
Esquema do Cenário: Cadastrar um aluno no banco de dados
    Dado que eu preencho o campo "nome" com "<nome>"
    E que eu preencho o campo "idade" com "<idade>"
    Quando eu salvo o formulário
    Então vejo a mensagem "Aluno <nome>, de <idade> anos foi cadastrado com sucesso!"

Exemplos:
    | nome    | idade |
    | Gabriel | 22    |
    | João    | 30    |
'''  # noqa

SCENARIO_OUTLINE2 = u'''
Esquema do Cenário: Cadastrar um aluno no banco de dados
    Dado que eu preencho o campo "nome" com "<nome>"
    E que eu preencho o campo "idade" com "<idade>"
    Quando eu salvo o formulário
    Então vejo a mensagem "Aluno <nome>, de <idade> anos foi cadastrado com sucesso!"

Cenários:
    | nome    | idade |
    | Gabriel | 99    |
    | João    | 100   |
'''  # noqa

FEATURE = u'''
Funcionalidade: Pesquisar alunos com matrícula vencida
  Como gerente financeiro
  Eu quero pesquisar alunos com matrícula vencida
  Para propor um financiamento

  Cenário: Pesquisar por nome do curso
    Dado que eu preencho o campo "nome do curso" com "Nutrição"
    Quando eu clico em "pesquisar"
    Então vejo os resultados:
      | nome  | valor devido |
      | João  | R$ 512,66    |
      | Maria | R$ 998,41    |
      | Ana   | R$ 231,00    |
'''


def parse_scenario(string, language=None):
    feature = """
Funcionalidade: parse_scenario
    """

    feature += string
    feature = Feature.from_string(feature, language=language)

    return feature.scenarios[0]


def test_language_portuguese():
    """
    Language: PT-BR -> Language class supports portuguese through code "pt-br"
    """

    lang = Language('pt-br')

    assert_equals(lang.code, u'pt-br')
    assert_equals(lang.name, u'Portuguese')
    assert_equals(lang.native, u'Português')
    assert_equals(lang.FEATURE, u'Funcionalidade')
    assert_equals(str(lang.SCENARIO),
                  u'{"Cenário" ^ "Cenario" ^ "Esquema do Cenário" ^ '
                  u'"Esquema do Cenario" ^ "Delineação do Cenário" ^ '
                  u'"Delineacao do Cenario"}')
    assert_equals(lang.EXAMPLES, u'Exemplos')


def test_scenario_ptbr_from_string():
    """
    Language: PT-BR -> Scenario.from_string
    """

    ptbr = Language('pt-br')
    scenario = parse_scenario(SCENARIO, language=ptbr)

    assert_equals(
        scenario.name,
        u'Consolidar o banco de dados de cursos universitários em '
        u'arquivo texto'
    )
    assert_equals(
        scenario.steps[0].hashes,
        [
            {'Nome': u'Ciência da Computação', u'Duração': '5 anos'},
            {'Nome': u'Nutrição', u'Duração': '4 anos'},
        ]
    )


def test_scenario_outline1_ptbr_from_string():
    """
    Language: PT-BR -> Scenario.from_string, with scenario outline, first case
    """

    ptbr = Language('pt-br')
    scenario = parse_scenario(SCENARIO_OUTLINE1, language=ptbr)

    assert_equals(
        scenario.name,
        'Cadastrar um aluno no banco de dados'
    )
    assert_equals(
        scenario.outlines,
        [
            {'nome': u'Gabriel', u'idade': '22'},
            {'nome': u'João', u'idade': '30'},
        ]
    )


def test_scenario_outline2_ptbr_from_string():
    """
    Language: PT-BR -> Scenario.from_string, with scenario outline, second case
    """

    ptbr = Language('pt-br')
    scenario = parse_scenario(SCENARIO_OUTLINE2, language=ptbr)

    assert_equals(
        scenario.name,
        'Cadastrar um aluno no banco de dados'
    )
    assert_equals(
        scenario.outlines,
        [
            {'nome': u'Gabriel', u'idade': '99'},
            {'nome': u'João', u'idade': '100'},
        ]
    )


def test_feature_ptbr_from_string():
    """
    Language: PT-BR -> Feature.from_string
    """

    ptbr = Language('pt-br')
    feature = Feature.from_string(FEATURE, language=ptbr)

    assert_equals(
        feature.name,
        u'Pesquisar alunos com matrícula vencida'
    )

    assert_equals(
        feature.description,
        u"Como gerente financeiro\n"
        u"Eu quero pesquisar alunos com matrícula vencida\n"
        u"Para propor um financiamento"
    )

    (scenario, ) = feature.scenarios

    assert_equals(
        scenario.name,
        'Pesquisar por nome do curso'
    )

    assert_equals(
        scenario.steps[-1].hashes,
        [
            {'nome': u'João', u'valor devido': 'R$ 512,66'},
            {'nome': u'Maria', u'valor devido': 'R$ 998,41'},
            {'nome': u'Ana', u'valor devido': 'R$ 231,00'},
        ]
    )
