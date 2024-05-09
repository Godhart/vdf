import pytest
import sys
from pathlib import Path
import ruamel.yaml
yaml = ruamel.yaml.YAML()
import json

vdf_root_path = str((Path(__file__).absolute().parent.parent.parent).resolve())
if vdf_root_path not in sys.path:
    sys.path.insert(0, vdf_root_path)

from tests.helpers import *
from src.helpers import *


def case1():
    import datetime
    class Dictable:
        def to_dict(self):
            return {"key1":"value1", "key2":"value2"}
    class TestClass:
        def __init__(self):
            self.int = 1
            self.str = "a string"
            self.float = 1.1
            self.bool = True
            self.complex = complex(0.2,0.3)
            self.void = None
            self.dict = {"key1":"value1", "key2":"value2"}
            self.list = [1,2,3]
            self.stringable = datetime.datetime.fromtimestamp(42.0, tz=datetime.timezone.utc)
            self.dictable = Dictable()
            self.nested_dict = {(1,):Dictable()}
            self.nested_list = [[4,5,6], Dictable()]
            self._hidden = "shouldn't see mee!"
            self.ref = self
            self.cls = Dictable

        @property
        def prop(self):
            return "it's a property"

    value = TestClass()
    return value


@pytest.mark.parametrize("test_set", list_tests(__file__, ["test","gold"]))
def test_any_to_dict_list_scalar(test_set):
    """
    Make sure that any to dict/list/scalar works properly
    """
    input_path, gold_path, output_path = init_test_paths(__file__, test_set)

    value = None
    if test_set == "case1":
        value = case1()

    result = any_to_dict_list_scalar(value)
    with open(output_path/"result.yaml", "w") as f:
        yaml.dump(result, f)
    with open(output_path/"result.json", "w") as f:
        f.write(json.dumps(result, indent=2))

    expected = [True, False][test_set[:4] == "err_"]

    assert same_as_gold(gold_path, output_path) == expected


if __name__ == "__main__":
    """
    NOTE: this branch is for debug purposes only
    """
    value = case1()
    result = any_to_dict_list_scalar(value)
