from .literals import *
from .source_io import SourceText, Line, Fenced
from .cells import Cell, CellsStream, CodeCell, DocCell


def is_vdf(kind:str|None, content:list[str]|list[Line]) -> bool:
    """
    Check if provided content is vdf cell
    """
    if kind is not None:
        if kind == S_VDF or kind[-1-len(S_VDF):] == "-"+S_VDF:
            return True

    if isinstance(content, (list, tuple)) and len(content) > 0:
        if isinstance(content[0], str):
            first_line = content[1]
        else:
            first_line = content[1].content
        if first_line[:len(C_VDF_PREAMBLE)] == C_VDF_PREAMBLE:
            return True

    return False


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
        if not self.autoparse:
            self.cells = None
            self.frontmatter = None

    @property
    def source(self) -> SourceText:
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
        step1 = []      # Lines are merged
        join_lines = 0  # If above zero - amount of chars to drop before joining following line
        for idx, line in source.lines:
            if join_lines > 0:
                step1[-1][1] = step1[-1][1][:-join_lines] + line
                join_lines = 0
            else:
                step1.append([idx, line,])
                idx +=1
            tmp = source.replace_escaped(line, '~')

            if tmp[-2:] == "\\\n":
                join_lines = 2
            if tmp[-3:] == "\\\r\n":
                join_lines = 3
            if tmp[-3:] == "\\\n\r":
                join_lines = 3


        ## Step 2.
        step2 = []  # list with Lines and Fenced sections
        fenced_idx = None
        fenced_end = None
        fenced_kind = None
        fenced_lines = []
        for idx, line in step1:
            if fenced_end is None:
                # If fenced section hasn't started yet
                fenced_end, fenced_kind = source.fenced_check(line.strip())
                if fenced_end is None:
                    step2.append((idx, line, Line(idx, line, source.source)))
                    continue
                else:
                    fenced_idx = idx
                    fenced_lines.append(Line(idx,line, source.source))
            else:
                # If inside fenced section
                fenced_lines.append(Line(idx,line, source.source))
                if line.strip() == fenced_end:
                    step2.append((
                        idx,
                        None,
                        Fenced(
                            fenced_idx,
                            fenced_kind,
                            fenced_lines,
                            source.source
                        ),
                    ))
                    fenced_idx = None
                    fenced_end = None
                    fenced_kind = None
                    fenced_lines = []
        if len(fenced_lines) > 0:
            # Last fenced section
            step2.append((
                idx,
                None,
                Fenced(
                    fenced_idx,
                    fenced_kind,
                    fenced_lines,
                    source.source
                ),
            ))

        # Step 3.
        step3 = []      # List of cells' content. Each item contains list of Lines and Fenced sections, related to a cell
        cell_data =  [] # Accumulated content for a single cell as a list
        i = -1
        split_ahead, split_skip = False, 0
        raw_lines = [v[1] for v in step2]
        while i < len(step2)-1:
            i += 1

            # Check if following sequence is cells split
            split_ahead, next_split_skip = source.split_ahead(raw_lines, i)
            if split_ahead:
                # Put accumulated into cells list, start new cell
                if len(cell_data) > 0:
                    cell_source = cell_data[0].source
                else:
                    cell_source = step2[i][2].source
                step3.append((cell_data, cell_source))
                cell_data = []
                split_skip = next_split_skip - 1
                continue

            # If part of split sequence should be skipped - skip it
            if split_skip > 0:
                split_skip -= 1
                continue

            # Accumulate data for next cell
            cell_data.append(step2[i][2])

        if len(cell_data) > 0:
            # Last cell
            step3.append((cell_data, cell_data[0].source))
            cell_data = []

        cells = []
        for cell_data, cell_source in step3:
            cells.append(Cell(
                cell_data,
                cell_source,
            ))

        result = CellsStream(cells)

        return result

    def raw_cells_stream_preprocess(
            self,
            raw_cells_stream: CellsStream
        ) -> tuple[CellsStream, Cell]:
        """
        Parse stream of raw cells into specialized cells and frontmatter
        """
        # 1. Check tags within cells, determine cell type
        # 2. Produce cells stream depending on their type

        result_cells = []
        raw_cells = raw_cells_stream.cells
        frontmatter = None

        if self.source.frontmatter and len(raw_cells) > 1:
            if len(raw_cells[0].content) > 0 \
            and isinstance(raw_cells[0].content[0], Line) \
            and raw_cells[0].content[0].content.strip() == "---":
                frontmatter = raw_cells[0]
                raw_cells = raw_cells[1:]

        for cell in raw_cells:
            stripped_cell_content = [
                v for v in cell.content
                if not isinstance(v, Line)
                or len(v.content.strip()) > 0
            ]
            if len(stripped_cell_content) == 1 and isinstance(stripped_cell_content[0], Fenced):
                result_cells.append(CodeCell(stripped_cell_content, cell.location)) # TODO: wtf this for? , name=cell.name))
            else:
                result_cells += self.raw_cell_process(cell)

        result = CellsStream(result_cells)
        return result, frontmatter

    def raw_cell_process(self, cell:Cell) -> list[DocCell|CodeCell]:
        """
        Parse raw cell into list of Doc/Code cells
        """
        result = []
        doc_items = []
        for item in cell.content:
            if isinstance(item, Line):
                doc_items.append(item)
                continue
            # It's fenced section
            if is_vdf(item.kind, item.content):
                # If it's vdf then it CodeCell
                if len(doc_items) > 0:
                    result.append(DocCell(doc_items, doc_items[0].source))
                doc_items = []
                result.append(CodeCell([item], item.source))
            else:
                doc_items.append(item)
        # Last doc item (if there is any)
        if len(doc_items) > 0:
            result.append(DocCell(doc_items, doc_items[0].source))
        doc_items = []
        return result

    def parse(self):
        """
        Parse attached source into internal objects (cells and frontmatter)
        Result data is saved internally
        """
        raw_cells = self.lines_to_raw_cells_stream(self.source)
        self.cells, self.frontmatter = self.raw_cells_stream_preprocess(raw_cells)

    @staticmethod
    def parse_code_content(first_line:str, content:str) -> CodeCell:
        """
        Parse lines of code cell into CodeCell
        This is the case for Jupyter code cells
        """
        lines = [
            first_line,
            *[l+"\n" for l in content.split("\n")],
        ]
        lines = \
              [Line(None, "``````````````````````````````````````````", ["Notebook"])] \
            + [Line(i,v, ["Notebook"]) for i,v in enumerate(lines)] \
            + [Line(None, "``````````````````````````````````````````", ["Notebook"])]
        fenced = Fenced(0, 'vhdl', lines, ["Notebook"])
        result = CodeCell(
            content = [fenced],
            location= ["Notebook"],  # TODO: get GUID of the cell
        )
        return result
