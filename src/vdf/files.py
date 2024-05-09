from pathlib import Path
import ruamel.yaml
yaml = ruamel.yaml.YAML()
from .literals import *
from ..helpers import *
from .context import RunContext, GeneratedLine
from . import files_render

_RENDERS   = (files_render, )

FILE_KIND_TXT           = "text"
FILE_KIND_MARKDOWN      = "markdown"
FILE_KIND_VHDL          = "vhdl"
FILE_KIND_VHDL_PACKAGE  = "vhdl_package"
FILE_KIND_VERILOG       = "verilog"
FILE_KIND_VERILOG_HEADER= "verilog_header"
FILE_KIND_SV            = "sv"
FILE_KIND_SV_HEADER     = "sv_header"


class FileSpec:
    """
    Defines output file specification
    """
    def __init__(
            self,
            render:     str,
            ext:        str,
            sections:   list[str],
            template:   str,
    ):
        if isinstance(render, str):
            if render[:1] == "_":
                raise ValueError(
                    f"Can use only public methods / classes, got '{render}'!")
            render_obj = None
            for v in _RENDERS:
                if hasattr(v, render):
                    render_obj = getattr(v, render)
            if render_obj is None:
                raise ValueError(
                    f"File Render with name '{render}'"
                    " wasn't found within tags runners!")
            render = render_obj
        self.render = render
        self.ext        = ext
        self.sections   = ['raw'] + sections
        self.template   = template


def load_file_formats(path:str) -> dict[str:FileSpec]:
    """
    Load file formats description from YAML file
    """
    with open(path, "rb") as f:
        data = yaml.load(f)
    for k,v in data[C_FALLBACK].items():
        for format_ in data:
            if format_ == C_FALLBACK:
                continue
            if k not in data[format_]:
                data[format_][k] = v
    result = {}
    for format_ in data:
        if format_ == C_FALLBACK:
            continue
        result[format_] = FileSpec(**data[format_])
    return result


FILE_FORMATS = load_file_formats(Path(__file__).parent / "files.yaml")


class File:
    """
    Represents current file state
    contains sections, that are modified via tags
    """
    @unsafe
    def __init__(
            self,
            path:str,
            kind:str=FILE_KIND_TXT,
            encoding:str='utf-8',
            eol:str='\n',
            file_spec:FileSpec|None=None,
            sections_data:dict=None,
            vars:       dict|None = None,
    ):
        self._path = path
        self.kind = kind
        if file_spec is None:
            if kind not in FILE_FORMATS:
                raise ValueError(
                    f"No spec for file kind '{kind}' were found!")
            file_spec = FILE_FORMATS[kind]
        self._file_spec = file_spec
        self.encoding = encoding
        self.eol = eol
        if sections_data is not None:
            for k in sections_data:
                if k not in self._file_spec.sections:
                    raise ValueError(
                        f"Unexpected section '{k}' in sections_data!")
            for k in self._file_spec.sections:
                if k not in sections_data:
                    raise ValueError(
                        f"Section '{k}' is missing in sections_data!")
            # TODO: moar sanity check
            self.sections_data = sections_data
        else:
            self.sections_data = {k:{} for k in self._file_spec.sections}
        # First key of sections data - section name
        # Second key - subsection name (to group parts of code within section)
        self.rendered = None  # Rendered lines or None
        self.vars = vars or {}
        self._render = self._file_spec.render()

    @property
    def path(self) -> str:
        return self._path + self._file_spec.ext

    def get_template(self) -> str:
        return self._file_spec.template

    def modify(
            self,
            section:str,
            value:list[GeneratedLine],
            subsection=C_DEFAULT,
            append=True
    ):
        if section not in self._file_spec.sections:
            raise ValueError(f"No section '{section}' in file '{self.path}'!")
        # NOTE: if raw section content is defined, other are banned
        #       if any section other than raw is defined - ban raw
        if section == S_RAW:
            subsection = C_DEFAULT    # NOTE: only one subsection in raw
            for k,v in self.sections_data.items():
                if k == S_RAW:
                    continue
                if any(len(vv) > 0 for vv in v.values()):
                    raise ValueError(
                        f"Other than '{S_RAW}' sections were specified before."
                        " Mixing raw and other code sections is not allowed!")
        else:
            if S_RAW in self.sections_data \
            and len(self.sections_data[S_RAW].get(C_DEFAULT, [])) > 0:
                raise ValueError(
                    f"'{S_RAW}' section were specified before."
                    " Mixing raw and other code sections is not allowed!")
        if subsection == C_ALL and append:
            raise ValueError(f"Append is not allowed with subsection '{C_ALL}'!")
        if subsection != C_ALL \
        and subsection not in self.sections_data[section]:
            self.sections_data[section][subsection] = []
        if not append:
            if subsection == C_ALL:
                self.sections_data[section] = {}
                # TODO: line below is not so obvious... doc it or remove it
                subsection = C_DEFAULT
            self.sections_data[section][subsection] = [] + value
        else:
            self.sections_data[section][subsection] += value

    def render(self, context:RunContext):
        """
        Render structured content into flat text
        NOTE: rendered data is kept internally and contains extra info
        To get final result - use saves or save
        """
        self.rendered = None
        self.rendered = self._render.render(self, context)

    def saves(self, flow=None) -> tuple[list[str], list[str]]:
        """
        Save final result into list of strings
        Mapping with info about line's sources is saved along
        """
        if self.rendered is None:
            self.render()
        lines = []
        lines_map = []
        for l  in self.rendered:
            f_line = self._render.finalize_line(l, flow)
            if f_line is None:
                continue
            line, l_map = f_line
            lines.append(line)
            lines_map.append(l_map)
        return lines, lines_map

    def save(self, output_path, flow=None, save_map=True) -> bool:
        """
        Save final result into file by specified path
        Mapping with info about line's sources is saved along
        """
        if self.rendered is None:
            self.render()
        lines, lines_map = self.saves(flow)
        file_path = Path(output_path) / self.path
        map_path = Path(output_path) / f"{self.path}.map"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            file_path.unlink()
        if map_path.exists():
            map_path.unlink()
        lines_encoded = self.eol.join(lines).encode(self.encoding)
        with open(file_path, "wb") as f:
            f.write(lines_encoded)
        if save_map:
            with open(map_path, "w") as f:
                f.writelines(lines_map)
        return True


class InnerFile(File):
    """
    File that were totally constructed internally
    Allows to set sections parts individually
    """


class OuterFile(File):
    """
    File that were loaded externally and then modified in some way
    Allows only to work with file as whole
    """

    def modify(
            self,
            section:str,
            value:list[GeneratedLine],
            subsection=C_DEFAULT,
            append=True
    ):
        if section != S_RAW:
            raise ValueError(
                f"Section other than '{S_RAW}'"
                f" is not allowed for '{self.path}'!")
        super(OuterFile, self).modify(section, value, subsection, append)


class Files:
    """
    Represents files collection
    """

    def __init__(self, files:list[File]):
        self._files = files

    @property
    def list(self):
        return self._files


def default_target(lang:str) -> tuple[str, str]|None:
    """
    Returns tuple if default file name and file kind for given language
    """
    if lang == S_MARKDOWN:
        return ("main", FILE_KIND_MARKDOWN)
    if lang == S_VHDL:
        return ("main", FILE_KIND_VHDL)
    if lang == S_VERILOG:
        return ("main", FILE_KIND_VERILOG)
    if lang == S_TEXT:
        return ("main", FILE_KIND_TXT)
    return None
