from copy import deepcopy
from hashlib import md5
from .literals import *
from .source_io import Line, Fenced
from .tags import TagsInstances
from .context import RunContext

class Cell:
    """
    Class for single cell representation
    """

    def __init__(self,
            content         : list[Line|Fenced],
            location        : list,
            input_context   : RunContext|None = None,
            tags            : TagsInstances|None = None,
            name            : str|None = None,
    ):
        self._content = content
        self._name = name
        self._hash = None
        self._location = location
        self.input_context = input_context
        self.run_context = deepcopy(input_context)
        self.output_context = deepcopy(input_context)
        self.tags = tags
        self.stdout = []    # Accumulated stdout of tags
        self.stderr = []    # Accumulated stderr of tags
        self.value = None   # Resulting value (if there is any)

    @property
    def cell_kind(self) -> str:
        return S_BASE_CELL

    @property
    def content(self):
        return [*self._content]

    @property
    def name(self) -> str:
        if self._name is not None:
            return self._name
        location = self._location
        if self.location is None or len(self.location) == 0:
            location =  ["Undefined"]
        return "_"+":".join([str(v) for v in location])

    @property
    def location(self) -> list:
        return [*self._location]

    @property
    def hash(self) -> str:
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
    def cell_kind(self) -> str:
        return S_DOC_CELL


class CodeCell(Cell):
    """
    Class for code-related cell representation
    """
    @property
    def cell_kind(self) -> str:
        return S_CODE_CELL


class CellsStream:
    """
    Class for representation source file as stream of cells
    """
    def __init__(self, cells:list[Cell]):
        self.cells = cells
