from .input import Fenced as _Fenced
from .tags import TagInstance as _TagInstance
from .tags import TagsInstances as _TagsInstances
from .context import RunContext as _RunContext


class _TagRunnerResult:
    """
    Class with results for tag run
    """
    def __init__(self, data:_Fenced, stdout:list[str], stderr:list[str], value):
        self.data   = data
        self.stdout = stdout
        self.stderr = stderr
        self.value  = value


class _TagRunner:
    """
    Base class for tag runners
    """
    # Set with tuples for mandatory args definitions.
    # Each tuple contains name of optional kwarg and value class
    mandatory_kwargs = set()

    # Set with tuples for optional args definitions.
    # Each tuple contains name of optional kwarg, value class and default value.
    optional_kwargs = set()

    def __init__(self,
            tag: _TagInstance, optional_tags:_TagsInstances, data:_Fenced, context:_RunContext):
        self._tag = tag
        self._data = data
        self._optional_tags = optional_tags
        self._context = context
        mandatory_left = [v for _,v in self.mandatory_kwargs]
        optional_fallback = {k:v for k,_,v in self.optional_kwargs}
        for k, v in tag.vars.items():
            arg_found = False
            for args_set in (mandatory_left, optional_fallback):
                if k not in args_set:
                    continue
                arg_found = True
                v = args_set[k][1](v)
                setattr(self, f"_{k}", v)
                if k in mandatory_left:
                    del mandatory_left[k]
                if k in optional_fallback:
                    del optional_fallback[k]
                
            if not arg_found:
                raise ValueError(f"Argument with name '{k}' is not supported!")
        if len(mandatory_left) > 0:
            raise ValueError(f"Some mandatory args were not set! ("+', '.join(mandatory_left)+")")
        for k, v in optional_fallback.items():
            setattr(self, f"_{k}", v)

    def run():
        data_out = None
        stdout = None
        stderr = None
        value = None
        return _TagRunnerResult(data_out, stdout, stderr, value)


class TagTest1:
    """
    Class to test tag specifications
    """
    mandatory_kwargs = set([
        "mandatory_arg",
    ])
    optional_kwargs = set([
        ("var_name",    "var_value"),
        ("optional_arg", "optional_arg_default"),
    ])


class TagCode(_TagRunner):
    """
    Code updater tag
    """
    mandatory_kwargs = set([
        "section",
    ])
    optional_kwargs = set([
        ("content",     "both"),
    ])

    def __init__(self, data:_Fenced, subtags, optional_tags, context, **kwargs):
        self._
        super(TagCode, self).__init__(data, subtags, optional_tags, context, **kwargs)


def tag_display(data: _Fenced, subtags, optional_tags, context):
    """
    Run expression, display expression result
    """
    stdout = None
    value = None
    return value, stdout, value


def tag_show(data: _Fenced, subtags, optional_tags, context):
    """
    Display accumulated results from previous code cell run
    """
