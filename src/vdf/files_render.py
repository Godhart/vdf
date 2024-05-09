from pathlib import Path
from copy import deepcopy
import io
import json
import ruamel.yaml
yaml = ruamel.yaml.YAML()
from jinja2.sandbox import SandboxedEnvironment
from .literals import *
from ..helpers import *
from .context import RunContext, GeneratedLine


class _FileRender:
    """
    Renders sections of file into file content
    Also makes references of generated lines to their source
    """
    def __init__(self):
        self._cleanup()

    def _cleanup(self):
        """
        Reset to defaults internal data
        """
        self._prepared_sections = None
        self._prepared_data = None

    @staticmethod
    def _to_yaml(value, margins:int=0, **kwargs) -> str:
        """
        Helper to convert value to yaml dict/list/scalar string in renders
        """
        yaml_raw = io.BytesIO()
        yaml.dump(value, yaml_raw, **kwargs)
        yaml_lines = yaml_raw.getvalue().decode()
        if margins > 0:
            margin = " "*margins
            yaml_lines = "\n".join([margin + l for l in yaml_lines.split("\n")])
        return yaml_lines

    def _render_section(
            self,
            sections:dict[str:list[GeneratedLine]],
            section_name:str,
            not_exists_ok:bool=True,
    ) -> str:
        """
        Renders single section of file to a string
        Uses all subsections, sorted by their names, _default_ first
        """
        if section_name not in sections:
            if not_exists_ok:
                return ""
            else:
                raise ValueError(f"Section '{section_name}' is not found!")
        result = []
        for line in sections[section_name]:
            result.append(self._render_line(line))
        return "\n".join(result)

    @critical_todo
    def _prepare(self, file, context:RunContext) -> dict:
        """
        Creates sandbox environment for using in renders
        Environment contains
        - main data to be rendered as
          dict(sections) of dict(subsections) of list of lines
        - vars as dict
        - attrs as dict
        - helpers
        """
        sections = {}
        for section, subsections in file.sections_data.items():
            subsections_keys = sorted(
                [k for k in subsections.keys() if k != C_DEFAULT])
            if C_DEFAULT in subsections:
                subsections_keys = [C_DEFAULT] + subsections_keys
            for sub in subsections_keys:
                for line in subsections[sub]:
                    if section not in sections:
                        sections[section] = []
                    sections[section].append(line)

        def render_section(section_name:str, margin:str="", not_exists_ok:bool=True):
            lines = self._render_section(sections, section_name, not_exists_ok)
            if margin != "":
                lines = "\n".join([margin + l for l in lines.split("\n")])
            return lines

        vars = {**file.vars}
        if S_SUBJECT not in vars:
            vars[S_SUBJECT] = Path(file.path).stem
            # TODO: not so obvious, doc it or remove it!
        data = to_dict(
            sections = sections,
            vars = EzClass(**deepcopy(vars)),
            global_vars = EzClass(**deepcopy(context.vars.data)),
            global_attrs = EzClass(**deepcopy(context.attrs.data)),
            yaml = self._to_yaml,
            json = json.dumps,
            str = str,
            render_section = render_section,
        )
        self._prepared_sections = sections
        self._prepared_data     = data

    def _render(self, template:str) -> list[str]:
        """
        Exact rendering function
        """
        raise NotImplementedError(
            "This function should be implemented in derivative class!")

    def _render_line(self, line:GeneratedLine) -> str:
        """
        Single line rendering
        """
        data = to_dict(
            line = line.content,
            source = any_to_dict_list_scalar(line.source),
            context = any_to_dict_list_scalar(line.source)
        )
        return C_RENDER_MAGIC+json.dumps(data, separators=(',', ':'))

    def render(self, file, context:RunContext) -> list[str]:
        """
        Render file structured data into flat lines using provided context
        NOTE: rendered lines contains extra info
        To get final result - use finalize_line for each line
        """
        self._prepare(file, context)
        result = self._render(file.get_template())
        self._cleanup()
        return result

    @critical_todo
    def finalize_line(self, line:str, flow=None) -> tuple[str, str]|None:
        """
        Remove extra info from line
        Returns pure line and mapping info (with description of line's source)
        """
        if C_RENDER_MAGIC not in line:
            return line, "[[Template]]"
        offs = line.index(C_RENDER_MAGIC)
        data = json.loads(line[offs + len(C_RENDER_MAGIC):])
        if flow is not None:
            raise NotImplementedError(
                "Flow separation is not implemented yet!")
            # TODO: check flow, skip if line is for different flow
            return None
        return \
            line[:offs] + data['line'], \
            json.dumps(data['source'], separators=(',', ':')),


class RenderJinja2(_FileRender):
    """
    Renders files using Jinja2
    """

    def _render(self, template:str) -> list[str]:
        """
        Render template using jinja
        """
        if S_RAW in self._prepared_data['sections']:
            template = "{% render_section('raw') %}"
        jinja = SandboxedEnvironment()
        result = jinja.from_string(template).render(**self._prepared_data)
        result = result.split("\n")
        return result

    def _render_line(self, line:GeneratedLine) -> str:
        """
        Preprocess each line using jinja
        Then call original method
        """
        content = line.content
        prev_content = None
        jinja = SandboxedEnvironment()  # TODO: use common env?
        while content != prev_content:
            prev_content = content
            content = jinja.from_string(prev_content).render(**self._prepared_data)
        j_line = GeneratedLine(content, line.source, line.context)
        return super(RenderJinja2, self)._render_line(j_line)
