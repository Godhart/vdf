from pathlib import Path
import yaml


class _FileRender:
    """
    Renders sections of file into file content
    Also makes references of generated lines to their
    """
    def flatten(self, file):
        """
        Puts data from file sections all-together into flat list
        Override this function for format-specific rendering
        """
        result = []
        result_map = []
        i = 0
        for k, section_data in file.sections_data.items():
            for sk in sorted(section_data.keys()):
                subsection_data = section_data[sk]
                for v in subsection_data:
                    i+=1
                    result.append(v.value)
                    result_map.append([i, *[str(vv) for vv in v.source_line_location]])
        return result, result_map

    def save(self, file, lines, lines_map, output_path=None):
        """
        Saves rendered data into file
        Also creates lines map file to find source of resulting line
        """
        if output_path is not None:
            if lines is not None:
                with open(Path(output_path) / file.path, "wb") as f:
                    f.write("\n".join(lines).encode(file.encoding))
            if lines_map is not None:
                with open(Path(output_path) / (file.path + ".map.yaml"), "wb") as f:
                    yaml.safe_dump(lines_map, f)


class RenderGeneric(_FileRender):
    """
    Nothing more than in base class
    """


class RenderVHDL(_FileRender):
    """
    Makes VHDL File
    """


class RenderVerilog(_FileRender):
    """
    Makes Verilog / System Verilog File
    """
