from pathlib import Path
import yaml
from . import files_render
from .source_io import GeneratedLine
from .literals import *

_RENDERS   = (files_render, )

FILE_KIND_TXT           = "text"
FILE_KIND_MARKDOWN      = "markdown"
FILE_KIND_VHDL          = "vhdl"
FILE_KIND_VHDL_PACKAGE  = "vhdl_package"
FILE_KIND_VERILOG       = "verilog"
FILE_KIND_VERILOG_HEADER= "verilog_header"
FILE_KIND_SV            = "sv"
FILE_KIND_SV_HEADER     = "sv_header"


def load_file_formats(path):
    with open(path, "rb") as f:
        data = yaml.safe_load(f)
    for k,v in data[S_FALLBACK].items():
        for format_ in data:
            if format_ == S_FALLBACK:
                continue
            if k not in data[format_]:
                data[format_][k] = v
    return data


FILE_FORMATS = load_file_formats(Path(__file__).parent / "files.yaml")


class File:
    """
    Represents current file state
    contains sections, that are modified via tags
    """
    def __init__(
            self,
            path:str,
            kind:str=FILE_KIND_TXT,
            encoding:str='utf-8',
            eol:str='\n',
            file_spec:dict=None,
            sections_data:dict=None
    ):
        self.path = path
        self.kind = kind
        if file_spec is None:
            if kind not in FILE_FORMATS:
                raise ValueError(f"No spec for file kind '{kind}' were found!")
            file_spec = FILE_FORMATS(kind)
        self.sections = file_spec[S_SECTIONS]

        render = file_spec[S_RENDER]
        if isinstance(render, str):
            if render[:1] == "_":
                raise ValueError(f"Can use only public methods / classes, got '{render}'!")
            render_obj = None
            for v in _RENDERS:
                if hasattr(v, render):
                    render_obj = getattr(v, render)
            if render_obj is None:
                raise ValueError(f"File Render with name '{render}' wan't found within tags runners!")
            render = render_obj
        self.render = render

        self.encoding = encoding
        self.eol = eol
        if sections_data is not None:
            for k in sections_data:
                if k not in self.sections:
                    raise ValueError(f"Unexpected section '{k}' in sections_data!")
            for k in self.sections:
                if k not in sections_data:
                    raise ValueError(f"Section '{k}' is missing in sections_data!")
            # TODO: moar sanity check
            self.sections_data = sections_data
        else:
            self.sections_data = {k:{} for k in self.sections}
        # First key of sections data - section name
        # Second key - subsection name (to group parts of code within section)

    def modify(self, section:str, value:list[GeneratedLine], subsection="_default_", append=True):
        if section not in self.sections_data:
            raise ValueError(f"No section '{section}' in file '{self.path}'!")
        if subsection == "_all_" and append:
            raise ValueError("Append is not allowed with subsection '_all_'!")
        if subsection != "_all_" and subsection not in self.sections_data[section]:
            self.sections_data[section][subsection] = []
        if not append:
            if subsection == "_all_":
                self.sections_data[section] = {}
                subsection = "_default_"
            self.sections_data[section][subsection] = value
        else:
            self.sections_data[section][subsection] += value


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

    def modify(self, section:str, value:list[GeneratedLine], append=False):
        if section != "content":
            raise ValueError(f"Section other than 'content' is not allowed for '{self.path}'!")
        if append:
            raise ValueError(f"Append is not allowed for '{self.path}'!")
        self.sections_data[section] = value


class Files:
    """
    Represents files collection
    """

    def __init__(self, files:list[File]):
        self._files = files
