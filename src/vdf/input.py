from .source_io import SourceText, Line, Fenced
from .cells import Cell, CellsStream, CodeCell, DocCell


S_KIND      = "kind"
S_FENCED    = "fenced"
S_NAME      = "name"
S_LINE      = "line"
S_LINES     = "lines"
S_START     = "start"
S_END       = "end"


class RawDocument:
    """
    Class for raw source document representation and handling
    """
    def __init__(self,
            source:SourceText,
            autoparse:bool=True
    ):
        self.autoparse = autoparse
        self.source = source
        self.cells = None
        self.frontmatter = None

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value:SourceText):
        self._source = value
        self.cells = None
        if self.autoparse:
            self.parse()

    def lines_to_raw_cells_stream(self, source:SourceText) -> CellsStream:
        """
        Parse source into cells stream
        Returns CellsStream
        """

        # What to do:
        # 1. Merge multiline code
        # 2. Lookup for fenced code boundaries
        # 3. Split into raw cells

        ## Step 1.
        step1 = []  # Lines are merged
        join_lines = False
        for idx, line in source.lines:
            if join_lines:
                step1[-1][1] += line
            else:
                step1.append([idx, line,])
                idx +=1
            tmp = source.replace_escaped(line, '~')
            join_lines = (tmp[-2:] == "\\\n" or tmp[-3:] == "\\\r\n" or tmp[-3:] == "\\\n\r")


        ## Step 2.
        step2 = []  # list with Lines and Fenced sections
        fenced_idx = None
        fenced_end = None
        fenced_name = None
        fenced_lines = []
        for idx, line in step1:
            if fenced_end is None:
                # If fenced section hasn't started yet
                fenced_end, fenced_name = source.fenced_check(line.strip())
                if fenced_end is None:
                    step2.append(idx, line, Line(idx, line))
                    continue
                else:
                    fenced_idx = idx
                    fenced_lines.append(idx, line, Line(idx,line))
            else:
                # If inside fenced section
                fenced_lines.append((idx, line))
                if line.strip() == fenced_end:
                    step2.append(idx, None, Fenced(idx, {S_KIND:S_FENCED, S_NAME: fenced_name, S_LINES: fenced_lines, S_START: fenced_idx, S_END: idx+1}))
                    fenced_idx = None
                    fenced_end = None
                    fenced_name = None
                    fenced_lines = []
        if len(fenced_lines) > 0:
            # Last fenced section
            step2.append(idx, None, Fenced(idx, {S_KIND:S_FENCED, S_NAME: fenced_name, S_LINES: fenced_lines, S_START: fenced_idx, S_END: idx+1}))

        # Step 3.
        step3 = []      # List of cells' content. Each item contains list of Lines and Fenced sections, related to a cell
        cell_data =  [] # Accumulated content for a single cell as a list
        i = -1
        split_ahead, split_skip = False, 0
        while i < len(step2):
            i += 1

            # Check if following sequence is cells split
            split_ahead, split_skip = source.split_ahead(step2, i)
            if split_ahead:
                # Put accumulated into cells list, start new cell
                step3.append(cell_data)
                cell_data = []
                split_skip -= 1
                continue

            # If part of split sequence should be skipped - skip it
            if split_skip > 0:
                split_skip -= 1
                continue
            
            # Accumulate data for next cell
            cell_data.append(step2[i][2])

        if len(cell_data) > 0:
            # Last cell
            step3.append(cell_data)
            cell_data = []

        cells = []
        for cell_data in step3:
            cells.append(Cell(cell_data))

        result = CellsStream(cells)

        return result

    def raw_cells_stream_preprocess(self, raw_cells_stream: CellsStream) -> tuple[CellsStream, Cell]:
        """
        Parse stream of raw cells into specialized cells and frontmatter
        """
        # 1. Check tags within cells, determine cell type
        # 2. Produce cells stream depending on their type

        result_cells = []
        raw_cells = raw_cells_stream.cells
        frontmatter = None

        if self.source.frontmatter and len(raw_cells > 1):
            frontmatter = raw_cells[0]
            raw_cells = raw_cells[1:]

        for cell in raw_cells:
            stripped_cell_content = [
                v for v in cell.content
                if not isinstance(v, Line)
                or len(v.content.strip()) > 0
            ]
            if len(stripped_cell_content) == 1 and isinstance(stripped_cell_content[0], Fenced):
                cell_type = CodeCell
                cell_content = stripped_cell_content
            else:
                cell_type = DocCell
                cell_content = cell.content
            result_cells.append(cell_type(cell_content, cell.location))

        result = CellsStream(result_cells)
        return result, frontmatter

    def parse(self):
        """
        Parse attached source into internal objects (cells and frontmatter)
        """
        raw_cells = self.lines_to_raw_cells_stream(self.source)
        self.cells, self.frontmatter = self.raw_cells_stream_preprocess(raw_cells)

    @staticmethod
    def parse_code_content(first_line:str, content:str) -> CodeCell:
        lines = [
            first_line,
            *content.split("\n"),
        ]
        lines = \
              [Line(None, "``````````````````````````````````````````")] \
            + [Line(i,v) for i,v in enumerate(lines)] \
            + [Line(None, "``````````````````````````````````````````")]
        fenced = Fenced(0, lines)
        result = CodeCell(
            content = fenced,
            location= ["Unavailable"]
        )
        return result
