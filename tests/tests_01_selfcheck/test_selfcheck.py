import pytest
import sys
from pathlib import Path

vdf_root_path = str((Path(__file__).absolute().parent.parent.parent).resolve())
if vdf_root_path not in sys.path:
    sys.path.insert(0, vdf_root_path)

import src as vdf
from tests.helpers import *


@pytest.mark.parametrize("test_set", list_tests(__file__, ["test","gold"]))
def test_selfcheck(test_set):
    """
    Self-checking boilerplate for tests
    When used for actual tests:
    - populate test/gold folders with necessary data
    - replace copy_tree call with function/sequence under test 
    """
    input_path, gold_path, output_path = init_test_paths(__file__, test_set)

    copy_tree(input_path, output_path, dirs_exist_ok=True, hidden=False)

    expected = [True, False][test_set[:4] == "err_"]

    assert same_as_gold(gold_path, output_path) == expected
