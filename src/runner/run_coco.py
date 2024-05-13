from pathlib import Path
import shutil
from cocotb.runner import get_runner
from ..helpers import *


# # NOTE: in original file (https://github.com/cocotb/cocotb/blob/master/examples/simple_dff/test_dff.py
# it was like cocotb_tools). # TODO: Why?
# from cocotb_tools.runner import get_runner

SIM_PLUS_ARGS = to_dict(
    ghdl        = ["--vcd=waves.vcd"],
)

SIM_EXTRA_ENV = to_dict(
    icarus      = to_dict(WAVES=1),
)


@unsafe
def run(build_spec_path:str|Path):

    build_spec_path = Path(build_spec_path)
    build_spec_data = load_jyt(build_spec_path)

    sim = build_spec_data['hdl_sim']

    build_dir = Path(build_spec_data.get('build_dir', build_spec_path.parent) / ".build")
    test_dir  = Path(build_spec_data.get('build_dir', build_spec_path.parent) / ".run")
    if test_dir.exists():
        # TODO: safely cleanup build dir
        # TODO: don't clean on partial rebuild
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)

    # TODO: this is sim-depended part...
    if sim == 'ghdl':
        shutil.copy2(build_dir / "main", test_dir / "main")

    runner = get_runner(sim)

    plusargs = SIM_PLUS_ARGS.get(sim, [])
    extra_env = SIM_EXTRA_ENV.get(sim, {})

    runner.test(
        build_dir           = build_dir,
        test_module         = build_spec_data['cocotb_run_module'],
        hdl_toplevel_lang   = build_spec_data['hdl_toplevel_lang'],
        hdl_toplevel_library= build_spec_data['hdl_toplevel_library'],
        hdl_toplevel        = build_spec_data['hdl_toplevel'],

        parameters          = build_spec_data['hdl_toplevel_generics'],

        waves=True,
        verbose=True,

        test_dir            = test_dir,
        extra_env           = extra_env,
        plusargs            = plusargs,
        # test_args         = hdl_run_test_args,
        # testcase          = hdl_run_testcase,
        # seed              = hdl_run_seed,
    )
