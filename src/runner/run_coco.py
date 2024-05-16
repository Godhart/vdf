from pathlib import Path
import shutil
from cocotb.runner import get_runner
from ..vdf.literals import *
from ..helpers import *


# # NOTE: in original file (https://github.com/cocotb/cocotb/blob/master/examples/simple_dff/test_dff.py
# it was like cocotb_tools). # TODO: Why? cocotb.runner is experimental now, switch to cocotb_tools?
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

    build_dir = Path(
        build_spec_data.get('build_dir', build_spec_path.parent) / C_BUILD_PATH)
    run_dir   = Path(
        build_spec_data.get('run_dir', build_spec_path.parent) / C_RUN_PATH)
    if run_dir != build_dir:
        if run_dir.exists():
            # TODO: safely cleanup build dir
            # TODO: don't clean on partial rebuild
            shutil.rmtree(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)

        # TODO: this is sim-depended part...
        if sim == 'ghdl':
            # TODO: copy compiled binary from build dir to run dir
            raise NotImplementedError(
                "Different run dir and build dir are not supported"
                " for GHDL yet!")

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

        test_dir            = run_dir,
        extra_env           = extra_env,
        plusargs            = plusargs,
        # test_args         = hdl_run_test_args,
        # testcase          = hdl_run_testcase,
        # seed              = hdl_run_seed,
    )
