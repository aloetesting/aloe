# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falc達o <gabriel@nacaolivre.org>
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

from nose.exc import SkipTest
from nose.tools import with_setup

from tests.asserts import capture_output, assert_equals
from lettuce import Runner

current_dir = abspath(dirname(__file__))
join_path = lambda *x: join(current_dir, *x)


def test_output_with_success_colorless():
    "Language: zh-CN -> sucess colorless"

    with capture_output() as (out, _):
        runner = Runner(join_path('zh-CN', 'success', 'dumb.feature'), verbosity=3)
        runner.run()

    assert_equals(out.getvalue(), u"""
功能: 简单测试           # tests/functional/language_specific_features/zh-CN/success/dumb.feature:3
  什么都不做应该运行成功 # tests/functional/language_specific_features/zh-CN/success/dumb.feature:4

  #1\s
  场景: 什么都不做       # tests/functional/language_specific_features/zh-CN/success/dumb.feature:6
    假如 如果 什么都不做 # tests/functional/language_specific_features/zh-CN/success/dumb_steps.py:6

  ----------------------------------------------------------------------------

1 feature (1 passed)
1 scenario (1 passed)
1 step (1 passed)
""")


def test_output_of_table_with_success_colorless():
    """Language: zh-CN -> success table colorless"""

    with capture_output() as (out, _):
        runner = Runner(join_path('zh-CN', 'success', 'table.feature'), verbosity=3)
        runner.run()

    assert_equals(out.getvalue(), u"""
功能: 步骤中包含表格             # tests/functional/language_specific_features/zh-CN/success/table.feature:3
  简体中文表格步骤的成功测试     # tests/functional/language_specific_features/zh-CN/success/table.feature:4

  #1\s
  场景: 什么都不做的表格步骤测试 # tests/functional/language_specific_features/zh-CN/success/table.feature:6
    假如 如果 输入数据如下:      # tests/functional/language_specific_features/zh-CN/success/table_steps.py:6
      | id | 名称   |
      | 12 | 名称一 |
      | 64 | 名称二 |

  ----------------------------------------------------------------------------

1 feature (1 passed)
1 scenario (1 passed)
1 step (1 passed)
""")


def test_output_outlines_success_colorless():
    """Language: zh-CN -> success outlines colorless"""

    with capture_output() as (out, _):
        runner = Runner(join_path('zh-CN', 'success', 'outlines.feature'), verbosity=3)
        runner.run()

    assert_equals(out.getvalue(), u"""
功能: 中文场景模板                 # tests/functional/language_specific_features/zh-CN/success/outlines.feature:3
  中文场景模板图表测试             # tests/functional/language_specific_features/zh-CN/success/outlines.feature:4

  #1\s
  场景大纲: 用表格描述场景         # tests/functional/language_specific_features/zh-CN/success/outlines.feature:6

  Example #1:
    | 处理 | 输入 | 结果 |
    | 这个 | 什么 | 功能 |

    假如如果 输入是<输入>          # tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:13
    当执行<处理>时                 # tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:22
    那么得到<结果>                 # tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:31

  ----------------------------------------------------------------------------

  Example #2:
    | 处理 | 输入 | 结果 |
    | 这里 | 其他 | 一样 |

    假如如果 输入是<输入>          # tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:13
    当执行<处理>时                 # tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:22
    那么得到<结果>                 # tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:31

  ----------------------------------------------------------------------------

  Example #3:
    | 处理 | 输入 | 结果         |
    | 动作 | 数据 | unicode输出! |

    假如如果 输入是<输入>          # tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:13
    当执行<处理>时                 # tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:22
    那么得到<结果>                 # tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:31

  ----------------------------------------------------------------------------

1 feature (1 passed)
3 scenarios (3 passed)
9 steps (9 passed)
""")

def test_output_outlines_success_colorful():
    "Language: zh-CN -> sucess outlines colorful"

    with capture_output() as (out, _):
        runner = Runner(join_path('zh-CN', 'success', 'outlines.feature'), verbosity=4)
        runner.run()

    raise SkipTest("coloured output")

    assert_equals(
        out.getvalue(),
        u'\n'
        u"\033[1;37m特性: 中文场景模板           \033[1;30m# tests/functional/language_specific_features/zh-CN/success/outlines.feature:3\033[0m\n"
        u"\033[1;37m  中文场景模板图表测试       \033[1;30m# tests/functional/language_specific_features/zh-CN/success/outlines.feature:4\033[0m\n"
        u'\n'
        u"\033[1;37m  场景模板: 用表格描述场景   \033[1;30m# tests/functional/language_specific_features/zh-CN/success/outlines.feature:6\033[0m\n"
        u"\033[0;36m    如果 输入是<输入>        \033[1;30m# tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:13\033[0m\n"
        u"\033[0;36m    当 执行<处理>时          \033[1;30m# tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:22\033[0m\n"
        u"\033[0;36m    那么 得到<结果>          \033[1;30m# tests/functional/language_specific_features/zh-CN/success/outlines_steps.py:31\033[0m\n"
        u'\n'
        u"\033[1;37m  例如:\033[0m\n"
        u"\033[0;36m   \033[1;37m |\033[0;36m 输入\033[1;37m |\033[0;36m 处理\033[1;37m |\033[0;36m 结果        \033[1;37m |\033[0;36m\033[0m\n"
        u"\033[1;32m   \033[1;37m |\033[1;32m 什么\033[1;37m |\033[1;32m 这个\033[1;37m |\033[1;32m 功能        \033[1;37m |\033[1;32m\033[0m\n"
        u"\033[1;32m   \033[1;37m |\033[1;32m 其他\033[1;37m |\033[1;32m 这里\033[1;37m |\033[1;32m 一样        \033[1;37m |\033[1;32m\033[0m\n"
        u"\033[1;32m   \033[1;37m |\033[1;32m 数据\033[1;37m |\033[1;32m 动作\033[1;37m |\033[1;32m unicode输出!\033[1;37m |\033[1;32m\033[0m\n"
        u'\n'
        u"\033[1;37m1 feature (\033[1;32m1 passed\033[1;37m)\033[0m\n"
        u"\033[1;37m3 scenarios (\033[1;32m3 passed\033[1;37m)\033[0m\n"
        u"\033[1;37m9 steps (\033[1;32m9 passed\033[1;37m)\033[0m\n"
    )

