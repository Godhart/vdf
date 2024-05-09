from copy import deepcopy
from .literals import *
from ..helpers import *
from .input import Fenced as _Fenced
from .tags import TagInstance as _TagInstance
from .tags_phases import *
from .files import InnerFile, OuterFile, default_target
from .context import RunContext, GeneratedLine


class _TagRunnerResult:
    """
    Class with results for tag run
    """
    def __init__(
            self,
            tag: str,
            phase:str,
            stdout:list[str],
            stderr:list[str],
            value
    ):
        self.phase  = phase
        self.tag    = tag
        self.stdout = stdout
        self.stderr = stderr
        self.value  = value


class _TagRunner:
    """
    Base class for tag runners
    """
    # TODO: remove mandatory_kwargs and optional_kwargs as it's redundant
    # Set with tuples for mandatory args definitions.
    # Each tuple contains name of optional kwarg and value class
    mandatory_kwargs = set()

    # Set with tuples for optional args definitions.
    # Each tuple contains name of optional kwarg, value class and default value.
    optional_kwargs = set()

    @critical_todo
    def __init__(
            self,
            tag
    ):
        self._tag = tag
        if False:
            # TODO: remove code below since tag's vars may be updated after runner creation
            mandatory_left = [v for v,_ in self.mandatory_kwargs]
            optional_fallback = {k:v for k,_,v in self.optional_kwargs}
            for k, v in tag.vars.items():
                arg_found = False
                for args_set, args_data in (
                    (mandatory_left,    self.mandatory_kwargs),
                    (optional_fallback, self.optional_kwargs),
                ):
                    if k not in args_set:
                        continue
                    arg_found = True
                    v = v  # TODO: args_data[k][1](v)
                    setattr(self, f"_{k}", v)
                    if k in mandatory_left:
                        del mandatory_left[mandatory_left.index(k)]
                    if k in optional_fallback:
                        del optional_fallback[optional_fallback.index(k)]

                if not arg_found:
                    raise ValueError(f"Argument with name '{k}' is not supported!")
            if len(mandatory_left) > 0:
                raise ValueError(f"Some mandatory args were not set! ("+', '.join(mandatory_left)+")")
            for k, v in optional_fallback.items():
                setattr(self, f"_{k}", v)

    @staticmethod
    def defaults() -> dict|None:
        """
        Provide defaults for document's attributes subsection of this tag runner
        Return None if defaults are not required
        """
        return None

    def apply(
            self,
            phase: str,
            tag: _TagInstance,
            cell,
            def_lang: str,
    ) -> _TagRunnerResult:
        """
        Apply tag action according to context
        """
        stdout = None
        stderr = None
        value = None
        return _TagRunnerResult(tag.line, phase, stdout, stderr, value)

    @stub_alert
    def _get_lang(self, context:RunContext, def_lang:str) -> str:
        """
        Determine target language
        """
        return def_lang

    @critical_todo
    def _get_target(
            self,
            cell,
            context:RunContext,
            def_lang:str
    ) -> tuple[str, str]:
        """
        Determine target file
        """
        lang = self._get_lang(context, def_lang)
        target = None
        # TODO: get target from context
        # TODO: try to use subject if target is not defined
        if target is None:
            dt = default_target(lang)
            if dt is None:
                raise ValueError(
                    f"No default target for language '{lang}'!"
                    f" Specify target via tag 'target'")
            else:
                target_path, target_kind = dt
                # TODO: make sure no default target language were set in context
                # for current cell kind (Code/Doc)
        else:
            # TODO: determine target name/kind from target/lang
            raise ValueError("Not implemented yet!")
        # TODO: If default code file were defined already
        # (implicitly by the first #code tag)
        # make sure subject and/or kind or target
        # is defined for code tags with other lang
        return target_path, target_kind

    def _ensure_target(
            self,
            context:RunContext,
            path:str,
            kind:str,
            encoding:str,
            eol:str
    ) -> InnerFile:
        chk_file = InnerFile(path, kind, encoding, eol)
        lookup_file = None
        for v in context.files.list:
            if v.path == chk_file.path:
                lookup_file = v
        if lookup_file is None:
            context.files.list.append(chk_file)
            lookup_file = chk_file
        return lookup_file

    def _copy_file(
            self,
            path:str,
            context_from:RunContext,
            context_to:RunContext
    ):
        src_file = None
        for v in context_from.files.list:
            if v.path == path:
                src_file = v
        if src_file is None:
            raise ValueError(f"Path '{path}' is not found in source context")

        idx = 0
        while idx < len(context_to.files.list):
            if context_to.files.list[idx].path == path:
                break
        if idx < len(context_to.files.list):
            context_to.files.list[idx] = src_file
        else:
            context_to.files.list.append(src_file)

    @not_implemented
    def _copy_vars(
            self,
            context_from:RunContext,
            context_to:RunContext,
            filter:dict):
        """
        Copy vars from one context to another using filters to include/exclude
        """

    @not_implemented
    def _copy_attrs(
            self,
            context_from:RunContext,
            context_to:RunContext,
            filter:dict):
        """
        Copy attrs from one context to another using filters to include/exclude
        """


class TagTest1(_TagRunner):
    """
    Class to test tag specifications
    """
    mandatory_kwargs = set([
        ("mandatory_arg", str),
    ])
    optional_kwargs = set([
        ("var_name",        str, "var_value"),
        ("optional_arg",    str, "optional_arg_default"),
    ])


class TagCode(_TagRunner):
    """
    Code updater tag
    """
    mandatory_kwargs = set([
        (S_CONTENT,         list),
        (S_SECTION,         str),
        (S_ACTION,          str),
    ])

    @critical_todo
    def apply(
            self,
            phase: str,
            tag: _TagInstance,
            cell,
            def_lang: str,
    ) -> _TagRunnerResult:
        """
        Apply tag action according to context
        """
        stdout = None
        stderr = None
        value = None

        if phase not in (TAG_PHASE_CODE, TAG_PHASE_FIN):
            return _TagRunnerResult(tag.line, phase, stdout, stderr, value)

        # Determine output file name
        # Depends on
        #   - subject
        #   - lang
        #   - kind
        #   - target
        file_path, file_kind = self._get_target(
            cell, cell.run_context, def_lang)

        encoding = 'utf-8'  # TODO: get from attr
        eol = '\n' # TODO: get from attr
        file = self._ensure_target(
            cell.run_context,
            file_path,
            file_kind,
            encoding,
            eol,
        )

        if phase == TAG_PHASE_CODE:
            append = tag.vars[S_ACTION].value != S_NEW
            if S_SECTION in tag.vars:
                section_kind = tag.vars[S_SECTION].value
            else:
                section_kind = None
            section_parts = tag.vars[S_CONTENT].value

            if isinstance(section_parts, str):
                section_parts = [section_parts]
            section_parts_lines = {v:[] for v in section_parts}

            lines = cell.flat_lines()
            if cell.cell_kind == S_CODE_CELL:
                lines = lines[2:-1]

            spi = 0
            section_part = section_parts[spi]
            for l in lines:
                if l.content == "---\n" and len(section_parts) > 1:
                    spi += 1
                    if spi >= len(section_parts):
                        raise ValueError(
                            f"More divisions than sections in cell"
                            f" {cell.location}")
                    section_part = section_parts[spi]
                    continue
                source = l.source
                if not isinstance(l, GeneratedLine):
                    source = [source]
                source.append(cell.location+[S_CELL, tag.line, phase])
                section_parts_lines[section_part].append(
                    GeneratedLine(
                        content = l.content,
                        source  = source,
                        context = RunContext(
                            files   = None,
                            attrs   = deepcopy(cell.run_context.attrs),
                            vars    = deepcopy(cell.run_context.vars),
                            vdf_ver = cell.run_context.vdf_ver,
                        )
                    )
                )

            for section_part, section_part_lines in section_parts_lines.items():
                if section_kind is not None:
                    section = f"{section_kind}__{section_part}"
                else:
                    section = f"{section_part}"
                file.modify(
                    section=section,
                    value = section_part_lines,
                    append = append,
                    # TODO: subsection from attr
                )

        if phase == TAG_PHASE_FIN:
            self._copy_file(file.path, cell.run_context, cell.output_context)

        return _TagRunnerResult(tag.line, phase, stdout, stderr, value)



class TagAttr(_TagRunner):
    """
    Updates context's attributes
    """
    @not_implemented
    def apply(
            self,
            phase: str,
            tag: _TagInstance,
            cell,
            def_lang: str,
    ) -> _TagRunnerResult:
        ...


class TagDisplay(_TagRunner):
    """
    Run expression, display expression result
    """
    @not_implemented
    def apply(
            self,
            phase: str,
            tag: _TagInstance,
            cell,
            def_lang: str,
    ) -> _TagRunnerResult:
        ...


class TagShow(_TagRunner):
    """
    Display results in a specified form
    """
    @not_implemented
    def apply(
            self,
            phase: str,
            tag: _TagInstance,
            cell,
            def_lang: str,
    ) -> _TagRunnerResult:
        ...
