from .files import Files
from .cells import CellsStream


class RunContext:
    """
    Run Context
    Contains vars, cells's data etc.
    """
    def __init__(
            self,
            doc     :CellsStream,
            files   :Files,
            cells   :CellsStream,
            vars    :dict,
    ):
        self._doc   = doc
        self._files = files
        self._cells = cells
        self._vars  = vars

    @property
    def doc(self):
        return self._doc
    
    @property
    def files(self):
        return self._files
    
    @property
    def cells(self):
        return self._cells
    
    @property
    def vars(self):
        return self._vars
