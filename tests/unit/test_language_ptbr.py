# -*- coding: utf-8 -*-
"""
Test Portuguese (Brasilian) language parsing.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin,wildcard-import,unused-wildcard-import
from builtins import *
# pylint:enable=redefined-builtin,wildcard-import,unused-wildcard-import

from nose.tools import assert_equal

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
'''

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
'''

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
    """Parse a scenario, prefixing it with a feature header."""
    feature_str = """
Funcionalidade: parse_scenario
    """

    feature_str += string
    feature = Feature.from_string(feature_str, language=language)

    return feature.scenarios[0]


def test_scenario_ptbr_from_string():
    """
    Language: PT-BR -> Scenario.from_string
    """

    scenario = parse_scenario(SCENARIO, language='pt-br')

    assert_equal(
        scenario.name,
        u'Consolidar o banco de dados de cursos universitários em '
        u'arquivo texto'
    )
    assert_equal(
        scenario.steps[0].hashes,
        (
            {'Nome': u'Ciência da Computação', u'Duração': '5 anos'},
            {'Nome': u'Nutrição', u'Duração': '4 anos'},
        )
    )


def test_scenario_outline1_ptbr_from_string():
    """
    Language: PT-BR -> Scenario.from_string, with scenario outline, first case
    """

    scenario = parse_scenario(SCENARIO_OUTLINE1, language='pt-br')

    assert_equal(
        scenario.name,
        'Cadastrar um aluno no banco de dados'
    )
    assert_equal(
        scenario.outlines,
        (
            {'nome': u'Gabriel', u'idade': '22'},
            {'nome': u'João', u'idade': '30'},
        )
    )


def test_scenario_outline2_ptbr_from_string():
    """
    Language: PT-BR -> Scenario.from_string, with scenario outline, second case
    """

    scenario = parse_scenario(SCENARIO_OUTLINE2, language='pt-br')

    assert_equal(
        scenario.name,
        'Cadastrar um aluno no banco de dados'
    )
    assert_equal(
        scenario.outlines,
        (
            {'nome': u'Gabriel', u'idade': '99'},
            {'nome': u'João', u'idade': '100'},
        )
    )


def test_feature_ptbr_from_string():
    """
    Language: PT-BR -> Feature.from_string
    """

    feature = Feature.from_string(FEATURE, language='pt-br')

    assert_equal(
        feature.name,
        u'Pesquisar alunos com matrícula vencida'
    )

    assert_equal(
        feature.description,
        u"Como gerente financeiro\n"
        u"Eu quero pesquisar alunos com matrícula vencida\n"
        u"Para propor um financiamento"
    )

    (scenario, ) = feature.scenarios

    assert_equal(
        scenario.name,
        'Pesquisar por nome do curso'
    )

    assert_equal(
        scenario.steps[-1].hashes,
        (
            {'nome': u'João', u'valor devido': 'R$ 512,66'},
            {'nome': u'Maria', u'valor devido': 'R$ 998,41'},
            {'nome': u'Ana', u'valor devido': 'R$ 231,00'},
        )
    )
