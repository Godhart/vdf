import pytest
import sys
from pathlib import Path

vdf_root_path = str((Path(__file__).absolute().parent.parent.parent).resolve())
if vdf_root_path not in sys.path:
    sys.path.insert(0, vdf_root_path)

from tests.helpers import *
from src.helpers import *
from src.vdf.source_io import load_from_file
from src.vdf.input import RawDocument
from src.vdf.document import Document


def parse_input_file(input_path):
    result = {}
    result['source']    = source = load_from_file(input_path)
    result['preparsed'] = preparsed = RawDocument(source)
    result['doc'] = Document(
        source=preparsed.cells,
        frontmatter=preparsed.frontmatter,
        root_context=None,
    )

    return result


@pytest.mark.parametrize("test_set", list_tests(__file__, ["test","gold"]))
def test_parse_input_file(test_set):
    """
    Make sure that any to dict/list/scalar works properly
    """
    input_path, gold_path, output_path = init_test_paths(__file__, test_set)

    value = parse_input_file(input_path.relative_to(os.getcwd()) /"data.md")

    result = any_to_dict_list_scalar(value)
    save_jyt(result, output_path/"result.yaml")
    save_jyt(result, output_path/"result.json")

    expected = [True, False][test_set[:4] == "err_"]

    assert same_as_gold(gold_path, output_path) == expected


if __name__ == "__main__":
    """
    NOTE: this branch is for debug purposes only
    """
    value = test_parse_input_file("markdown-01-simple")
    result = any_to_dict_list_scalar(value)
    a = 1
