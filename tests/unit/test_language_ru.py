# -*- coding: utf-8 -*-
"""
Test Russian language parsing.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# pylint:disable=redefined-builtin,wildcard-import,unused-wildcard-import
from builtins import *
# pylint:enable=redefined-builtin,wildcard-import,unused-wildcard-import
from future import standard_library
standard_library.install_aliases()

from nose.tools import assert_equal
from aloe.parser import Feature

SCENARIO = u"""
Сценарий: Сохранение базы курсов универитета в текстовый файл
    Допустим имеем в базе университет следующие курсы:
       | Название                | Длительность  |
       | Матан                   | 2 года        |
       | Основы программирования | 1 год         |
    Когда я сохраняю базу курсову в файл 'курсы.txt'
    Тогда в первой строке файла 'курсы.txt' строку 'Матан:2'
    И во второй строке файла 'курсы.txt' строку 'Основы программирования:1'
"""

SCENARIO_OUTLINE1 = u'''
Структура сценария: Заполнение пользователей в базу
    Допустим я заполняю в поле "имя" "<имя>"
    И я заполняю в поле "возраст"  "<возраст>"
    Если я сохраняю форму
    То я вижу сообщени "Студент <имя>, возраст <возраст>, успешно занесен в базу!"

Примеры:
    | имя  | возраст |
    | Вася | 22      |
    | Петя | 30      |
'''  # noqa

FEATURE = u'''
Функционал: Деление чисел
  Поскольку деление сложный процесс и люди часто допускают ошибки
  Нужно дать им возможность делить на калькуляторе

  Сценарий: Целочисленное деление
    Допустим я беру калькулятор
    Тогда я делю делимое на делитель и получаю частное
    | делимое | делитель | частное |
    | 100     | 2        | 50      |
    | 28      | 7        | 4       |
    | 0       | 5        | 0       |
'''


def parse_scenario(string, language=None):
    """Parse a scenario, prefixing it with a feature header."""
    feature = u"""
    Функция: parse_scenario
    """
    feature += string
    feature = Feature.from_string(feature, language=language)

    return feature.scenarios[0]


def test_scenario_ru_from_string():
    """
    Language: RU -> Scenario.from_string
    """

    scenario = parse_scenario(SCENARIO, language='ru')

    assert_equal(
        scenario.name,
        u'Сохранение базы курсов универитета в текстовый файл'
    )
    assert_equal(
        scenario.steps[0].hashes,
        (
            {u'Название': u'Матан',
             u'Длительность': u'2 года'},
            {u'Название': u'Основы программирования',
             u'Длительность': u'1 год'},
        )
    )


def test_scenario_outline1_ru_from_string():
    """
    Language: RU -> Scenario.from_string, with scenario outline, first case
    """

    scenario = parse_scenario(SCENARIO_OUTLINE1, language='ru')

    assert_equal(
        scenario.name,
        u'Заполнение пользователей в базу'
    )
    assert_equal(
        scenario.outlines,
        (
            {u'имя': u'Вася', u'возраст': '22'},
            {u'имя': u'Петя', u'возраст': '30'},
        )
    )


def test_feature_ru_from_string():
    """
    Language: RU -> Feature.from_string
    """

    feature = Feature.from_string(FEATURE, language='ru')

    assert_equal(
        feature.name,
        u'Деление чисел'
    )

    assert_equal(
        feature.description,
        u"Поскольку деление сложный процесс и люди часто допускают ошибки\n"
        u"Нужно дать им возможность делить на калькуляторе"
    )

    (scenario, ) = feature.scenarios

    assert_equal(
        scenario.name,
        u'Целочисленное деление'
    )

    assert_equal(
        scenario.steps[-1].hashes,
        (
            {u'делимое': '100', u'делитель': '2', u'частное': '50'},
            {u'делимое': '28', u'делитель': '7', u'частное': '4'},
            {u'делимое': '0', u'делитель': '5', u'частное': '0'},
        )
    )
