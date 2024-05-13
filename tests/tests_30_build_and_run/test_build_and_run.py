import pytest
import sys
from pathlib import Path
import ruamel.yaml
yaml = ruamel.yaml.YAML()
import json
import shutil

vdf_root_path = str((Path(__file__).absolute().parent.parent.parent).resolve())
if vdf_root_path not in sys.path:
    sys.path.insert(0, vdf_root_path)

from tests.helpers import *
from src.helpers import *
from tests.tests_10_read_the_doc.test_read_the_doc import parse_input_file
from src.vdf.document import Document
from src.vdf.processing import VdfProcessor
from src.builder.build_coco import build
from src.runner.run_coco import run


def preprocess_input_file(doc:Document, output_path:str) -> dict[str:dict]:
    stages = VdfProcessor().process_doc(doc)
    files = {}
    order = -1
    curdir = Path(os.curdir).absolute()
    for f in stages[-1][2].output_context.files.list:
        f.save(output_path, flow=None)
        order += 1
        files[f.path] = to_dict(
            path = str((Path(output_path) / f.path).resolve().absolute().relative_to(curdir)),
            lib = "top",
            order = order,
        )
    return files


def save_build_spec(build_data:dict, output_path:str|Path) -> Path:
    spec_path = Path(output_path) / "build_spec.yaml"
    with open(spec_path, "w") as f:
        yaml.dump(build_data, f)
    return spec_path


@pytest.mark.parametrize("test_set", list_tests(__file__, ["test","gold"]))
def test_build_and_run(test_set:str):
    """
    Make sure that any to dict/list/scalar works properly
    """
    input_path, gold_path, output_path = init_test_paths(__file__, test_set)

    doc = parse_input_file(input_path.relative_to(os.getcwd()) /"data.md")['doc']
    sources = preprocess_input_file(doc, output_path)
    top = "main"
    build_spec = to_dict(
        sources = sources,

        # RTL Sim Common Spec
        hdl_sim = "ghdl",                   # TODO: define it somewhere. Also verilator / icarus / questa is possible

        hdl_toplevel_lang = "vhdl",         # TODO: define it somewhere. Also verilog is possible
        hdl_toplevel_library = "top",       # TODO: define it somewhere.
        hdl_toplevel = top,
        hdl_toplevel_generics = {},         # TODO: generics for top

        # CoCoTB Specific Spec              # TODO: depends on sim
        cocotb_run_module = "src.runner.run_coco_test_module",
    )
    spec_path = save_build_spec(build_spec, output_path)

    # TODO: run with popen, get stdout, stderr
    build(spec_path)

    # TODO: run with popen, get stdout, stderr
    run(spec_path)

    # NOTE: waves.vcd contains header with run date (first 3 lines), drop it
    skip = False
    with open(output_path / ".run" / "waves.vcd", "r") as fr:
        with open(output_path / "waves.vcd", "w") as fw:
            v = None
            while v != "":
                v = fr.readline()
                if v == "$date\n":
                    skip=True
                if not skip:
                    fw.write(v)
                if v == "$end\n":
                    skip=False

    expected = [True, False][test_set[:4] == "err_"]

    assert same_as_gold(
        gold_path,
        output_path,
        ignore=[
            ".build",
            ".build/*",
            ".build/**/*",
            ".run",
            ".run/*",
            ".run/**/*",
        ],
    ) == expected


if __name__ == "__main__":
    """
    NOTE: this branch is for debug purposes only
    """
    value = test_build_and_run("markdown-vhdl-01-simple")
    result = any_to_dict_list_scalar(value)
    a = 1
