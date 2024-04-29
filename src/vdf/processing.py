from .cells import Cell, CodeCell, DocCell
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
        #  - depends on whether it's code or doc cell
        #  - make sure every tag is enabled
        #  - look for cell name and check it's unique
        # Determine into which branch / flow cell should fall
        # Get context from branch
        # Make temporary altered context by side tags (alter tags and vars)
        # Process cell according to context and tags
        #   - convert data if there is #convert tag
        # Put cell into branch / flow

        # NOTE: it's possible that cell is in a raw text form
        # (this would be the case if called by Jupyter's magic)
        # If so - convert text into ad-hoc cell
        if isinstance(cell, tuple):
            cell = RawDocument.parse_code_content(*cell)

        # TODO: var's scopes

        # Determine output file name
        # Depends on
        #   - subject
        #   - lang
        #   - kind
        #   - target

        # If default code file were defined already (implicitly by the first #code tag)
        # make sure subject and/or kind or target is defined for code tags with other lang

    def initialize_doc(
        self,
        document    : Document
    ):
        """
        Initialize documents context
        """
        # Run through all tags and run their's init code

        # TODO: update tags like
        # fetch
        #

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
