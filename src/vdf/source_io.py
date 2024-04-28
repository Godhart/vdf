import re
import yaml
from pathlib import Path
from ..helpers import *
from .literals import *


def load_source_formats(path):
    with open(path, "rb") as f:
        data = yaml.safe_load(f)
    for k,v in data[S_FALLBACK][S_SPEC].items():
        for format_ in data:
            if format_ == S_FALLBACK:
                continue
            if S_SPEC not in data[format_]:
                data[format_][S_SPEC] = {}
            if k not in data[format_][S_SPEC]:
                data[format_][S_SPEC][k] = v
    return data


SOURCE_FORMATS = load_source_formats(Path(__file__).parent / "source_formats.yaml")
SOURCE_ENCODING = ['utf-8',]


class SourceReader:
    """
    Class for reading data from misc sources
    """


class SourceText:
    """
    Class for ops with text source
    """
    def __init__(self,
            source          :list,
            lines           :list[str],
            format          :str=S_MARKDOWN,
            escape_symbol   :str|None=None,
            fenced_seq      :str|None=None,
            fenced_regex    :str|None=None,
            cells_split     :list[str]|None=None,
            frontmatter     :bool|None=None,
    ):
        self._source = [*source]
        self._lines = list(enumerate(lines))
        self.format = format

        # NOTE: set dummy values for type-hinting as actual values are applied in generalized way
        self.escape_symbol  = ""
        self.fenced_seq     = ""
        self.fenced_regex   = ""
        self.cells_split    = [""]
        self.frontmatter    = True

        spec = to_dict(
            escape_symbol   = escape_symbol,
            fenced_seq      = fenced_seq,
            fenced_regex    = fenced_regex,
            cells_split     = cells_split,
            frontmatter     = frontmatter,
        )
        for k,v in spec.items():
            spec[k] = v or SOURCE_FORMATS[format][S_SPEC][k]
            setattr(self, k, spec[k])
            
    @property
    def source(self):
        return [*self._source]

    @property
    def lines(self):
        """
        List of lines
        Each item is tuple of two with
        - line index in a source, starting from zero
        - line content
        """
        return self._lines

    def replace_escaped(self, line, replacement_char):
        """
        Replaces escaped chars in line with replacement_char
        """
        if self.escape_symbol is None:
            return line
        result = ""
        prev = None
        for char in line:
            if prev == self.escape_symbol:
                result += replacement_char
                prev = replacement_char
            else:
                result += char
                prev = char
        return result

    def fenced_check(self, line):
        """
        Checks that line is a start of fenced section.
        If so - full fence sequence and fenced type are returned
        Otherwise None,None is returned
        """
        if line[:len(self.fenced_seq)] == self.fenced_seq:
            m = re.match(self.fenced_regex, line)
            if m is not None:
                return m.groups()
        else:
            return None, None

    def split_ahead(self, lines, offs):
        """
        Checks that lines starting from offs are cells split sequence
        Returns tuple of two with
        - True/False as check result
        - length of split sequence in lines
        """
        lookup = lines[offs:offs+len(self.cells_split)]
        split_skip = 0
        split_detected = False
        if None not in lookup:
            lookup = [v.strip() for v in lookup]
            split_detected = lookup == self.cells_split
            if split_detected:
                split_skip = len(self.cells_split)
        return split_detected, split_skip


class SourceBinary:
    """
    Class for ops with binary source
    """


class Line:
    """
    Stands for every single line in text file
    """
    def __init__(self, idx:int, content:str, source:list):
        self.idx = idx
        self.content = content
        self.source = source + [idx]


class GeneratedLine:
    """
    Class contains generated line data and reference
    to source that was used to produce it
    """
    def __init__(self, value, source_line_location: list):
        self.value = value
        self.source_line_location = [*source_line_location]
        # NOTE: source line location is rather abstract but recommended content is:
        # - VDF file location
        # - cell location (starting line of cell within VDF file)
        # - line location (starting line within cell's data)


class Fenced:
    """
    Contains all lines of fenced section 
    """
    def __init__(self, idx:int, kind:str, content:list[Line], source:list):
        self.idx = idx
        self.kind = kind
        self.content = [*content]
        self.source = source + [idx]


def load_from_file(path):
    path = Path(path)
    file_kind = None
    for k,v in SOURCE_FORMATS.items():
        if k == S_FALLBACK:
            continue
        if path.suffix in v[S_EXT]:
            file_kind = k
            break
    if file_kind is None:
        file_kind = "markdown"
    file_spec = SOURCE_FORMATS[file_kind][S_SPEC]
    if SOURCE_FORMATS[file_kind][S_KIND] == S_TEXT:
        with open(path, "rb") as f:
            data = f.read()
        lines = None
        for enc in SOURCE_ENCODING:
            try:
                lines = data.decode(enc)
            except:
                pass
        if lines is None:
            raise ValueError(
                f"Failed to decode data using provided encodings!"
                f" ({', '.join(SOURCE_ENCODING)})"
            )
        lines = lines.split("\n")
        lines = [l.replace("\r","") + "\n" for l in lines]
        result = SourceText([path], lines, file_kind, **file_spec)
    else:
        with open(path, "rb") as f:
            data = f.read()
        result = SourceBinary([path], data, file_kind, **file_spec)
    return result
