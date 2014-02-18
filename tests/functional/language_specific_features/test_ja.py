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
from nose.tools import with_setup
from tests.asserts import capture_output, assert_equals

from lettuce import Runner


current_dir = abspath(dirname(__file__))
join_path = lambda *x: join(current_dir, *x)


def test_output_with_success_colorless():
    """Language: ja -> success colorless"""

    with capture_output() as (out, err):
        runner = Runner(join_path('ja', 'success', 'dumb.feature'),
                        verbosity=3)
        runner.run()

    assert_equals(out.getvalue(),
        u"\n"
        u"フィーチャ: ダムフィーチャ           # tests/functional/language_specific_features/ja/success/dumb.feature:3\n"
        u"  テストをグリーンになればテスト成功 # tests/functional/language_specific_features/ja/success/dumb.feature:4\n"
        u"\n"
        u"  #1\s\n"
        u"  シナリオ: 何もしない               # tests/functional/language_specific_features/ja/success/dumb.feature:6\n"
        u"    前提 何もしない                  # tests/functional/language_specific_features/ja/success/dumb_steps.py:6\n"
        u"\n"
        u"  ----------------------------------------------------------------------------\n"
        u"\n"
        u"1 feature (1 passed)\n"
        u"1 scenario (1 passed)\n"
        u"1 step (1 passed)\n"
    )


def test_output_of_table_with_success_colorless():
    """Language: ja -> success table colorless"""

    with capture_output() as (out, err):
        runner = Runner(join_path('ja', 'success', 'table.feature'),
                        verbosity=3)
        runner.run()

    assert_equals(out.getvalue(),
        u"\n"
        u"フィーチャ: テーブル記法                     # tests/functional/language_specific_features/ja/success/table.feature:3\n"
        u"  日本語でのテーブル記法がパスするかのテスト # tests/functional/language_specific_features/ja/success/table.feature:4\n"
        u"\n"
        u"  #1\s\n"
        u"  シナリオ: 何もしないテーブル               # tests/functional/language_specific_features/ja/success/table.feature:6\n"
        u"    前提 データは以下:                       # tests/functional/language_specific_features/ja/success/table_steps.py:6\n"
        u"      | id | 定義       |\n"
        u"      | 12 | 何かの定義 |\n"
        u"      | 64 | 別の定義   |\n"
        u"\n"
        u"  ----------------------------------------------------------------------------\n"
        u"\n"
        u"1 feature (1 passed)\n"
        u"1 scenario (1 passed)\n"
        u"1 step (1 passed)\n"
    )


def test_output_outlines_success_colorless():
    """Language: ja -> success outlines colorless"""

    with capture_output() as (out, err):
        runner = Runner(join_path('ja', 'success', 'outlines.feature'),
                        verbosity=3)
        runner.run()

    assert_equals(out.getvalue(), u"""
フィーチャ: アウトラインを日本語で書く       # tests/functional/language_specific_features/ja/success/outlines.feature:3
  図表のテストをパスすること                 # tests/functional/language_specific_features/ja/success/outlines.feature:4

  シナリオテンプレ: 全てのテストで何もしない # tests/functional/language_specific_features/ja/success/outlines.feature:6
    前提 入力値を <データ1> とし             # tests/functional/language_specific_features/ja/success/outlines_steps.py:13
    もし 処理 <方法> を使って                # tests/functional/language_specific_features/ja/success/outlines_steps.py:22
    ならば 表示は <結果> である              # tests/functional/language_specific_features/ja/success/outlines_steps.py:31

  例:
    | データ1 | 方法 | 結果       |
    | 何か    | これ | 機能       |
    | その他  | ここ | 同じ       |
    | データ  | 動く | unicodeで! |

1 feature (1 passed)
3 scenarios (3 passed)
9 steps (9 passed)
    """)


def test_output_outlines_success_colorful():
    "Language: ja -> sucess outlines colorful"

    runner = Runner(join_path('ja', 'success', 'outlines.feature'), verbosity=4)
    runner.run()

    return

    assert_stdout_lines(
        u'\n'
        u"\033[1;37mフィーチャ: アウトラインを日本語で書く           \033[1;30m# tests/functional/language_specific_features/ja/success/outlines.feature:3\033[0m\n"
        u"\033[1;37m  図表のテストをパスすること                     \033[1;30m# tests/functional/language_specific_features/ja/success/outlines.feature:4\033[0m\n"
        u'\n'
        u"\033[1;37m  シナリオアウトライン: 全てのテストで何もしない \033[1;30m# tests/functional/language_specific_features/ja/success/outlines.feature:6\033[0m\n"
        u"\033[0;36m    前提 入力値を <データ1> とし                 \033[1;30m# tests/functional/language_specific_features/ja/success/outlines_steps.py:13\033[0m\n"
        u"\033[0;36m    もし 処理 <方法> を使って                    \033[1;30m# tests/functional/language_specific_features/ja/success/outlines_steps.py:22\033[0m\n"
        u"\033[0;36m    ならば 表示は <結果> である                  \033[1;30m# tests/functional/language_specific_features/ja/success/outlines_steps.py:31\033[0m\n"
        u'\n'
        u"\033[1;37m  例:\033[0m\n"
        u"\033[0;36m   \033[1;37m |\033[0;36m データ1\033[1;37m |\033[0;36m 方法\033[1;37m |\033[0;36m 結果      \033[1;37m |\033[0;36m\033[0m\n"
        u"\033[1;32m   \033[1;37m |\033[1;32m 何か   \033[1;37m |\033[1;32m これ\033[1;37m |\033[1;32m 機能      \033[1;37m |\033[1;32m\033[0m\n"
        u"\033[1;32m   \033[1;37m |\033[1;32m その他 \033[1;37m |\033[1;32m ここ\033[1;37m |\033[1;32m 同じ      \033[1;37m |\033[1;32m\033[0m\n"
        u"\033[1;32m   \033[1;37m |\033[1;32m データ \033[1;37m |\033[1;32m 動く\033[1;37m |\033[1;32m unicodeで!\033[1;37m |\033[1;32m\033[0m\n"
        u'\n'
        u"\033[1;37m1 feature (\033[1;32m1 passed\033[1;37m)\033[0m\n"
        u"\033[1;37m3 scenarios (\033[1;32m3 passed\033[1;37m)\033[0m\n"
        u"\033[1;37m9 steps (\033[1;32m9 passed\033[1;37m)\033[0m\n"
    )

