from .cells import Cell
from .document import Document


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
