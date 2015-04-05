from lychee import step, world


@step(r'I have entered (\d+) into the calculator')
def enter_number(self, number):
    if not hasattr(world, 'numbers'):
        world.numbers = []
    world.numbers.append(float(number))


@step(r'I press add')
def press_add(self):
    world.result = sum(world.numbers)


@step(r'The result should be (\d+) on the screen')
def assert_result(self, result):
    assert world.result == float(result)
