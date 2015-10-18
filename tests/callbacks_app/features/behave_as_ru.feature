# language: ru
Функция: behave_as

  Проверка работы behave_as на русском языке

  Контекст:
    Пусть I emit a step event of "Z"
    И I emit a step event for each letter in "BC"

  Сценарий: Проверка behave_as
    Пусть I emit a step event of "A"
    И I emit a step event for each letter in "DE"
    # Last two brackets are from the current example
    Тогда the step event sequence should be "{[Z]}{[{[B]}{[C]}]}{[A]}{[{[D]}{[E]}]}{["
