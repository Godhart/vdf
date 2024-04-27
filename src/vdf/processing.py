from .cells import Cell
from .document import Document


class GeneratedLine:
    """
    Class contains generated line data and reference to source that was used to produce it
    """
    def __init__(self, value, source_line_location: list):
        self.value = value
        self.source_line_location = source_line_location
        # NOTE: source line location is rather abstract but recommended content is:
        # - VDF file location
        # - cell location (starting line of cell within VDF file)
        # - line location (starting line within cell's data)


class VdfProcessor:
    """
    Handles VDF magic
    """
    def process_cell(
        self,
        document    : Document,
        cell        : Cell|tuple[str, list[str]],
    ):
        # TODO: describe what to do
        raise NotImplementedError("TODO:")
