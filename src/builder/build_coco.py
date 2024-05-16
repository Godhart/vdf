from pathlib import Path
import shutil
from cocotb.runner import get_runner
from ..vdf.literals import *
from ..helpers import *


SUPPORTED_LANG = to_dict(
    ghdl        = ['vhdl'],
    verilator   = ['verilog', 'sv'],
    icarus      = ['verilog', 'sv'],
    questa      = ['vhdl', 'verilog', 'sv'],
)


@unsafe
def build(build_spec_path:str|Path):

    build_spec_path = Path(build_spec_path)
    build_spec_data = load_jyt(build_spec_path)

    sim = build_spec_data['hdl_sim']

    build_stages = []

    current_stage_lang = None
    current_stage_lib = None

    for local_path, source_data in sorted(
        build_spec_data['sources'].items(), key=lambda x: x[1]['order']
    ):
        if Path(local_path).suffix.lower() in ('.vhd', '.vhdl'):
            file_lang = 'vhdl'
            file_lib  = source_data['lib']
        elif Path(local_path).suffix.lower() in ('.v', '.vh',):
            file_lang = 'verilog'
            file_lib  = 'verilog'
        elif Path(local_path).suffix.lower() in ('.sv', '.svh'):
            file_lang = 'sv'
            file_lib  = 'sv'
        else:
            raise ValueError(f"No info how to build {local_path}!")

        if sim in SUPPORTED_LANG:
            if file_lang not in SUPPORTED_LANG[sim]:
                raise ValueError(f"Simulator '{sim}' doesn't supports language '{file_lang}'!")

        if file_lang == 'sv':
            file_lang = 'verilog'
            file_lib  = 'verilog'

        if file_lang != current_stage_lang or file_lib != current_stage_lib:
            current_stage_lang = None
            current_stage_lib = None

        if current_stage_lang is None or current_stage_lib is None:
            build_stages.append(to_dict(
                lang = file_lang,
                lib  = file_lib,
                sources = []
            ))
            current_stage_lang = file_lang
            current_stage_lib  = file_lib

        build_stages[-1]['sources'].append(source_data['path'])

    build_dir = Path(build_spec_data.get('build_dir', build_spec_path.parent) / C_BUILD_PATH)
    if build_dir.exists():
        # TODO: safely cleanup build dir
        # TODO: don't clean on partial rebuild
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    runner = get_runner(sim)

    for bs in build_stages:
        if bs['lang'] == 'vhdl':
            verilog_sources = []
            vhdl_sources    = bs['sources']
            hdl_library     = bs['lib']
        else:
            verilog_sources = bs['sources']
            vhdl_sources    = []
            hdl_library     = 'top' # NOTE: Fallback value that is used by cocotb
        runner.build(
            build_dir       = build_dir,
            hdl_library     = hdl_library,
            verilog_sources = verilog_sources,
            vhdl_sources    = vhdl_sources,

            verbose         = True,
            always          = True,    # TODO: build only necessary files to reduce build time

            defines         = build_spec_data.get('hdl_build_defines', {}),
            build_args      = build_spec_data.get('hdl_build_args', []),
            includes        = build_spec_data.get('hdl_build_includes', []),
            parameters      = build_spec_data.get('hdl_build_parameters', {}),
        )

    # Build finally top level
    runner.build(
        build_dir       = build_dir,
        hdl_library     = build_spec_data['hdl_toplevel_library'],
        hdl_toplevel    = build_spec_data['hdl_toplevel'],
        verilog_sources = [],
        vhdl_sources    = [],

        verbose         = True,
        always          = True,    # TODO: build only necessary files to reduce build time

        defines         = build_spec_data.get('hdl_build_defines', {}),
        build_args      = build_spec_data.get('hdl_build_args', []),
        includes        = build_spec_data.get('hdl_build_includes', []),
        parameters      = build_spec_data.get('hdl_build_parameters', {}),
    )
