# from .files import Files


class Vars:
    """
    Variables collection
    Class is required since complex things like scope would be used
    """
    def __init__(self, vars:dict):
        self.data = vars
        # TODO: var's scopes


class Attrs:
    """
    Attributes collection
    Class to handle things that can't be foreseen now
    """
    def __init__(self, attrs:dict):
        self.data = attrs


class RunContext:
    """
    Run Context
    Contains files, vars, cells's data etc.
    """
    def __init__(
            self,
            files   ,               # All produced files,
            # NOTE: type=.files.Files, but not type-hinted due to circular ref error
            vars    :Vars,          # All the variables
            attrs   :Attrs,         # All the tag-defined attributes
            vdf_ver :str,           # Used VDF spec version
    ):
        self._files = files
        self._vars  = vars
        self._attrs  = attrs
        self.vdf_ver = vdf_ver

    @property
    def files(self):
        return self._files

    @property
    def vars(self) -> Vars:
        return self._vars

    @property
    def attrs(self) -> Attrs:
        return self._attrs


class GeneratedLine:
    """
    Class contains generated line data and reference
    to source that was used to produce it
    """
    def __init__(self,
            content :str,
            source  :list[list],
            context :RunContext
    ):
        self.content = content
        self.source = [*source]
        self.context = context
        # NOTE: source line location is rather abstract
        # but recommended content is:
        # - VDF file location
        # - cell location (starting line of cell within VDF file)
        # - line location (starting line within cell's data)
