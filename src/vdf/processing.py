from .cells import Cell
from .input import RawDocument
from .document import Document
from .literals import *


class VdfProcessor:
    """
    Handles VDF magic
    """
    # TODO: init section with defines to processor (if necessary)

    def process_cell(
        self,
        document    : Document,
        cell        : Cell,
    ):
        """
        Process cell depending on it's content and current document state
        """
        # Take current state of document
        # Take cell
        # Detect tags in cell
        # Determine into which branch / flow cell should fall
        # Get context from branch
        # Process cell according to context and tags
        # Put cell into branch / flow

        # NOTE: it's possible that cell is in a raw text form
        # (this would be the case if called by Jupyter's magic)
        # If so - convert text into ad-hoc cell
        if isinstance(cell, tuple):
            cell = RawDocument.parse_code_content(*cell)

    def initialize_doc(
        self,
        document    : Document
    ):
        """
        Initialize documents context
        """
        if document.frontmatter is not None:
            pass

    def process_doc(
        self,
        document    : Document
    ):
        """
        Initialize document's context and process all source cells
        """
        self.initialize_doc(document)
        for cell in document.source.cells:
            self.process_cell(document, cell)
