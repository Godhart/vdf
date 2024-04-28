# Classes for handling large VDF structures
from .cells import Cell, CellsStream


class Branch:
    """
    Class for representation chained cells
    """
    def __init__(self):
        self.stages = []        # Contains context for each branch stage


class Document:
    """
    Class for whole document representation
    """
    def __init__(self, source:CellsStream, frontmatter:Cell|None):
        self._frontmatter = frontmatter # Frontmatter part
        self._source = source           # Document's source cell's (cells that are not processed)
        self._branches = {}             # Registered cell's branches
        self._flows = {}                # Registered production flows
        
    @property
    def frontmatter(self):
        return self._frontmatter
    
    @property
    def source(self):
        return self._source

    @property
    def branches(self):
        return self._branches
    
    @property
    def flows(self):
        return self._flows
