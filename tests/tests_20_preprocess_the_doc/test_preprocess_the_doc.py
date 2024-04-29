import pytest
import sys
from pathlib import Path
import yaml
import json

vdf_root_path = str((Path(__file__).absolute().parent.parent.parent).resolve())
if vdf_root_path not in sys.path:
    sys.path.insert(0, vdf_root_path)

from tests.helpers import *
from src.helpers import *
from tests.tests_10_read_the_doc.test_read_the_doc import parse_input_file
from src.vdf.document import Document
from src.vdf.processing import VdfProcessor


def preprocess_input_file(doc:Document):
    VdfProcessor().process_doc(doc)
    return doc


@pytest.mark.parametrize("test_set", list_tests(__file__, ["test","gold"]))
def no_test_preprocess_the_doc(test_set):
    """
    Make sure that any to dict/list/scalar works properly
    """
    input_path, gold_path, output_path = init_test_paths(__file__, test_set)

    doc = parse_input_file(input_path.relative_to(os.getcwd()) /"data.md")['doc']
    value = preprocess_input_file(doc)

    result = any_to_dict_list_scalar(value)
    with open(output_path/"result.yaml", "w") as f:
        yaml.safe_dump(result, f, allow_unicode=True)
    with open(output_path/"result.json", "w") as f:
        f.write(json.dumps(result, indent=2))

    expected = [True, False][test_set[:4] == "err_"]

    assert same_as_gold(gold_path, output_path) == expected


if __name__ == "__main__":
    """
    NOTE: this branch is for debug purposes only
    """
    value = test_preprocess_the_doc("markdown-01-simple")
    result = any_to_dict_list_scalar(value)
    a = 1
