from .source_io import Line, Fenced, GeneratedLine
from .files import Files
from .tags import TagInstance, TagsInstances
from hashlib import md5


class Cell:
    """
    Class for single cell representation
    """

    def __init__(self,
            content         : list[Line|Fenced],
            location        : list,
            input_context     = None, # NOTE: type is RunContext, look below
            tags            : TagsInstances = None,
            name            : str|None = None,
    ):
        self._content = content
        self._name = name
        self._hash = None
        self._location = location
        self.input_context = input_context
        self.output_context = None
        self.tags = tags

    @property
    def cell_kind(self):
        return "Cell"

    @property
    def content(self):
        return [*self._content]

    @property
    def name(self):
        if self._name is not None:
            return self._name
        location = self._location
        if self.location is None or len(self.location) == 0:
            location =  ["Undefined"]
        return "_"+":".join([str(v) for v in location])

    @property
    def location(self):
        return [*self._location]

    @property
    def hash(self):
        """
        Return self's hash
        Cell's name doesn't affects hash
        """
        if self._hash is None:
            bytes = bytearray()
            for item in self._content:
                # TODO: exclude tag with cell's name
                if isinstance(item, Line):
                    bytes += item.content.encode()
                else:
                    for l in item.content:
                        bytes += l.content.encode()
            self._hash = md5(bytes).hexdigest()
        return self._hash

    def raw_lines(self) -> list[str]:
        result = []
        for v in self.content:
            result += v.raw_lines()
        return result

    def flat_lines(self) -> list[Line]:
        result = []
        for v in self.content:
            result += v.flat_lines()
        return result


class DocCell(Cell):
    """
    Class for documentation-related cell representation
    """
    @property
    def cell_kind(self):
        return "DocCell"


class CodeCell(Cell):
    """
    Class for code-related cell representation
    """
    @property
    def cell_kind(self):
        return "CodeCell"


class CellsStream:
    """
    Class for representation source file as stream of cells
    """
    def __init__(self, cells:list[Cell]):
        self.cells = cells


class Vars:
    """
    Variables collection
    Class is required since complex things like scope would be used
    """
    def __init__(self, vars:dict):
        self.data = vars
        # TODO: var's scopes


class Attrs:
    """
    Attributes collection
    Class to handle things that can't be foreseen now
    """
    def __init__(self, attrs:dict):
        self.data = attrs


class RunContext:
    """
    Run Context
    Contains vars, cells's data etc.
    """
    def __init__(
            self,
            doc     :CellsStream,   # DocCells
            files   :Files,         # All produced files
            code    :CellsStream,   # CodeCells
            vars    :Vars,          # All the variables
            attrs   :Attrs,         # All the tag-defined attributes
            vdf_ver :str,           # Used VDF spec version
    ):
        self._doc   = doc
        self._files = files
        self._code  = code
        self._vars  = vars
        self._attrs  = attrs
        self.vdf_ver = vdf_ver

    @property
    def doc(self):
        return self._doc

    @property
    def files(self):
        return self._files

    @property
    def code(self):
        return self._code

    @property
    def vars(self):
        return self._vars

    @property
    def attrs(self):
        return self._attrs
