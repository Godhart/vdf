"""
Cells Magic for Jupyter
"""
from IPython.core.magic import Magics, magics_class, line_cell_magic
import json
import ruamel.yaml
yaml = ruamel.yaml.YAML()
from tempfile import TemporaryDirectory

from ..vdf.literals import *
from ..helpers import *
from ..vdf.cells import Cell, CellsStream
from ..vdf.document import Document
from ..vdf.processing import VdfProcessor
from ..builder.build_coco import build
from ..runner.run_coco import run
from ..third_parties.vcd2json.vcd2json import WaveExtractor
# TODO: check also https://github.com/Toroid-io/vcd2wavedrom

from IPython.display import display, Markdown, clear_output
import ipywidgets as widgets

# TODO: explore moar widgets at https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20List.html


@magics_class
class VdfMagic(Magics):

    def __init__(self, shell, context:dict):
        super(VdfMagic, self).__init__(shell)
        self._context = context
        self._init_context()
        self._files_saved = False

    def _init_context(self, force:bool=False):
        if S_DOCUMENT not in self._context or force:
            vp = self._context[S_PROCESSOR] = VdfProcessor()
            doc = self._context[S_DOCUMENT] = vp.initialize_doc(Document(CellsStream([]), None, None))
            self._context[S_STAGES] = [(doc, None)]
            self._context[S_BUILD_DIR] = TemporaryDirectory()
            self._context[S_RUN_DIR] = self._context[S_BUILD_DIR]
            self._context[S_RUN] = None
            self._context[S_BUILD] = None

    def _load_stage(self, stage) -> tuple[Document|Cell]:
        return self._context[S_STAGES][stage]

    def _vp(self) -> VdfProcessor:
        return self._context[S_PROCESSOR]

    def _append_stage(self, doc:Document, cell: Cell):
        self._context[S_STAGES].append((doc, cell))

    def _build_dir(self) -> TemporaryDirectory:
        return self._context[S_BUILD_DIR]

    def _run_dir(self) -> TemporaryDirectory:
        return self._context[S_RUN_DIR]

    def _shows_tabs(self, tabs_data:dict[str:dict[str:str]]):
        for tab_group, tabs in tabs_data.items():
            if len(tabs_data) > 1:
                display(Markdown(f"### {tab_group}\n"))
            tabs_dict = {}
            for tab_id, tab_data in tabs.items():
                tabs_dict[tab_id] = widgets.Output()
            tabs_widget =  widgets.Tab(list(tabs_dict.values()))
            for i,title in enumerate(tabs_dict.keys()):
                tabs_widget.set_title(i, str(title))
            display(tabs_widget)
            for tab_content in tabs_dict.values():
                with tab_content:
                    # clear_output()
                    display(Markdown(tab_data))

    def _save(self):
        self._files_saved = False
        bd = self._build_dir()
        bd.cleanup()
        save_path = Path(bd.name)
        _, c = self._load_stage(-1)
        for f in c.output_context.files.list:
            f.save(save_path, flow=None)
        # TODO: make symlinks to external files
        self._files_saved = True

    def _get_files(self) -> dict[str:dict]:
        _, c = self._load_stage(-1)
        if c is None:
            return

        bd = self._build_dir()
        save_path = Path(bd.name)

        files = {}
        order = 0
        for f in c.output_context.files.list:
            order += 1
            files[f.path] = to_dict(
                path = str((save_path / f.path).absolute().resolve()),
                lib = "top",    # TODO: lib may vary
                order = order,  # TODO: order may vary
            )
        return files

    def _show(self, line:str, cell=None):
        if not self._files_saved:
            self._save()
        files = self._get_files()

        tabs_data = {}
        if "#show-src" in line or re.search("(\s|^)#show(\s|$)", line) is not None:
            sources = {}
            for k,v in files.items():
                src = []
                src.append("```vhdl")
                with open(v['path'], "r") as f:
                    src.append(f.read())
                src.append("```")
                sources[k] = "\n".join(src)
            if len(sources) > 0:
                tabs_data['Sources'] = sources

        if "#show-waves" in line:
            waves_data = ""
            if self._context[S_RUN] is None:
                waves_data = "> No simulation data!"
            elif S_WAVES not in self._context[S_RUN]:
                waves_data = "> No waves recorded!"
            elif cell is None:
                raise ValueError("No cell data!")
            else:
                waves_data = {}
                # TODO: https://github.com/wavedrom/vcdrom
                waves_spec = yaml.load(cell.encode())
                subst = {}
                for wave_group, waves_items in waves_spec.items():
                    if waves_items is None:
                        paths = []
                    else:
                        paths = [k for k in waves_items.keys() if k[:1] != "_"]
                        if C_PREFIX in waves_items:
                            subst = {waves_items[C_PREFIX] + k:k for k in paths}
                            paths = [waves_items[C_PREFIX] + k for k in paths]
                    vcd_path = str(self._context[S_RUN][S_WAVES])
                    json_path = str(self._context[S_RUN][S_WAVES])+f".{wave_group}.json"
                    extractor = WaveExtractor(vcd_path, json_path, paths)
                    for k in paths:
                        ks = subst.get(k,k)
                        v = waves_items[ks]
                        if v is not None:
                            extractor.wave_format(k, v)
                    # TODO: start-time / end-time
                    extractor.execute()
                    wave = load_jyt(json_path)
                    waves_data[wave_group] = f"""
<script type="WaveDrom">
{wave}
</script>
<script type="text/javascript">WaveDrom.ProcessAll()</script>
"""
            if isinstance(waves_data, str):
                waves_data={C_EXCEPTION: f"> {waves_data}"}
            if len(waves_data) > 0:
                # TODO: should be
                #   tabs_data[S_WAVES.capitalize()] = waves_data
                # but due to some bug need to show in different tabs groups
                for k,v in waves_data.items():
                    tabs_data[f"{S_WAVES.capitalize()}-{k}"] = {k:waves_data[k]}

        if "#tabs-single" in line:
            tmp = {}
            for k,v in tabs_data.items():
                for kk,vv in v.items():
                    kk = str(kk)
                    if kk in tmp:
                        kk = f"{k}-{kk}"
                    tmp[kk] = vv
            tabs_data = tmp

        self._shows_tabs(tabs_data)

    def _save_build_spec(self, build_data:dict, output_path:str|Path) -> Path:
        spec_path = Path(output_path) / "build_spec.yaml"
        save_jyt(build_data, spec_path)
        return spec_path

    def _build(self, line:str):
        if not self._files_saved:
            self._save()
        bd = self._build_dir()
        output_path = Path(bd.name)

        files = self._get_files()
        top = "main"
        build_spec = to_dict(
            sources = files,

            # RTL Sim Common Spec
            hdl_sim = "ghdl",                   # TODO: define it somewhere. Also verilator / icarus / questa is possible

            hdl_toplevel_lang = "vhdl",         # TODO: define it somewhere. Also verilog is possible
            hdl_toplevel_library = "top",       # TODO: define it somewhere.
            hdl_toplevel = top,
            hdl_toplevel_generics = {},         # TODO: generics for top

            # CoCoTB Specific Spec              # TODO: depends on sim
            cocotb_run_module = "src.runner.run_coco_main_module",
        )
        spec_path = self._save_build_spec(build_spec, output_path)
        # TODO: run with popen, get stdout, stderr
        build(spec_path)
        # TODO: update cell with run/build results
        return spec_path

    def _run(self, line:str):
        if not self._files_saved:
            self._save()
        bd = self._build_dir()
        output_path = Path(bd.name)

        spec_path = self._build(line)

        schedule = to_dict(
            max_runtime = 2.,
            min_simtime = "200  ns",
            max_simtime = "1000 ns",
            tasks = to_dict(
                sample_s = to_dict(
                    kind = "sample",
                    signals = ["s"],
                    trigger = "time",
                    trigger_options = [[10, "ns"], [20, "ns"], [30, "ns"], [40, "ns"]]
                )
            )
        )
        save_jyt(schedule, output_path / C_RUN_PATH / "runner_schedule.yaml")
        run(spec_path)
        self._context[S_RUN] = to_dict(waves=output_path / C_RUN_PATH / "waves.vcd")

    def _vdf_debug(self, line:str):
        bd = self._build_dir()
        result = []
        result.append(f"`build_dir` = `{bd.name}`")
        result = "\n".join(result)
        display(Markdown(result))

    def _line_magic(self, line:str):
        ## special tags processing
        # - #vdf-reset  to init dir
        if "#reset" in line:
            self._build_dir().cleanup()
            self._run_dir().cleanup()
            self._init_context(force=True)

        # - #vdf-load-N to load Nth cell result
        if "#load-" in line:
            # TODO: set stage to necessary
            raise NotImplementedError("#vdf-load is not supported yet!")

        if "#build" in line:
            self._build(line)

        if "#run" in line:
            self._run(line)

        if "#show" in line:
            self._show(line)

        # - #vdf-debug to print debug info
        if "#vdf-debug" in line:
            self._vdf_debug(line)

        if "#wavedrom" in line:
            # TODO: use cdn
            wave_script_load = ""
            wave_script_load += '<script src="https://wavedrom.com/skins/default.js"></script>'
            wave_script_load += '<script src="https://wavedrom.com/skins/dark.js"></script>'
            wave_script_load += '<script src="https://wavedrom.com/skins/narrow.js"></script>'
            wave_script_load += '<script src="https://wavedrom.com/skins/lowkey.js"></script>'
            wave_script_load += '<script src="https://wavedrom.com/wavedrom.min.js"></script>'
            display(Markdown(wave_script_load))

    @line_cell_magic
    def vdf(self, line:str, cell=None):
        if cell is None:
            self._line_magic(line)
            return

        if "#wave" in line:
            wave_data = cell
            if "#format-yaml" in line:
                wave_data = json.dumps(yaml.load(wave_data.encode()))
            wave_out = f"""
<script type="WaveDrom">
{wave_data}
</script>
<script type="text/javascript">WaveDrom.ProcessAll()</script>
"""
            display(Markdown(wave_out))
            return

        if "#show-wave" in line:
            self._show(line, cell)
            return

        doc, _ = self._load_stage(-1)
        vp = self._vp()
        d, c = vp.process_cell(doc, ("%%vdf "+line,cell))
        self._files_saved = False
        self._context[S_BUILD] = None
        self._context[S_RUN] = None

        if "#build" in line:
            self._build(line)

        if "#run" in line:
            self._run(line)

        if "#show" in line:
            self._show(line, cell)

        if "#vdf-tmp" not in line:
            # TODO: don't save cells if processing/build/run failed
            self._append_stage(d, c)

        # - #vdf-debug to print debug info
        if "#vdf-debug" in line:
            self._vdf_debug(line)

        # TODO: break if processing/build/run failed


    # TODO: look on InteractiveShell usage
    # get_ipython() # we can get the current InteractiveShell
    # https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.interactiveshell.html
    # - user_ns: The user namespace (a dictionary).
    # - push(): Push (or inject) Python variables in the interactive namespace.
    # - ev(): Evaluate a Python expression in the user namespace.
    # - ex(): Execute a Python statement in the user namespace.
    # - run_cell(): Run a cell (given as a string), possibly containing IPython magic commands.
    # - safe_execfile(): Safely execute a Python script.
    # - system(): Execute a system command.
    # - write(): Write a string to the default output.
    # - write_err(): Write a string to the default error output.
    # - register_magic_function(): Register a standalone function as an IPython magic function. We used this method in this recipe.

    # https://ipython.readthedocs.io/en/stable/config/extensions/autoreload.html