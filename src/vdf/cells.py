from .source_io import Line, Fenced
from .processing import GeneratedLine
from .context import RunContext
from .files import Files
from .tags import TagInstance, TagsInstances


class Cell:
    """
    Class for single cell representation
    """

    def __init__(self,
            content         : list[Line|Fenced],
            location        : list,
            input_context   : RunContext = None,
            tag             : TagInstance = None,
            optional_tags   : TagsInstances = None,
            name            : str|None = None,
    ):
        self._content = content
        self._name = name
        self._location = location
        self.input_context = input_context
        self.output_context = RunContext(
            files=Files([]),
            cells=CellsStream([]),
            vars ={},
        )
        self.tag = tag
        self.optional_tags = optional_tags

    @property
    def content(self):
        return [*self.content]

    @property
    def name(self):
        if self._name is not None:
            return self._name
        location = self._location
        if self.location is None or len(self.location) == 0:
            location =  ["Undefined"]
        return ":".join([str(v) for v in location])

    @property
    def location(self):
        return [*self._location]

    @property
    def hash(self):
        """
        Return self's hash (which includes hash of cell parent(s))
        Cell's name doesn't affects hash
        """
        raise NotImplementedError("Not implemented yet!")


class DocCell(Cell):
    """
    Class for documentation-related cell representation
    """


class CodeCell(Cell):
    """
    Class for code-related cell representation
    """


class CellsStream:
    """
    Class for representation source file as stream of cells
    """
    def __init__(self, cells:list[Cell]):
        self.cells = cells
