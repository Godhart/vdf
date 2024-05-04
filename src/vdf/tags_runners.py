from .input import Fenced as _Fenced
from .tags import TagInstance as _TagInstance
from .tags import TagsInstances as _TagsInstances


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

    def __init__(
            self,
            tag: _TagInstance,
            data:_Fenced,
            context,
    ):
        # NOTE: context is a RunContext but due to circular refs is not typehinted
        self._tag = tag
        self._data = data
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

    @staticmethod
    def defaults():
        """
        Provide defaults for document's attributes subsection of this tag runner
        Return None if defaults are not required
        """
        return None

    def apply():
        """
        Apply tag action according to context
        """
        data_out = None
        stdout = None
        stderr = None
        value = None
        return _TagRunnerResult(data_out, stdout, stderr, value)


class TagTest1(_TagRunner):
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

    def __init__(
            self,
            tag: _TagInstance,
            data:_Fenced,
            context,
            **kwargs
    ):
        super(TagCode, self).__init__(tag, data, context, **kwargs)


class TagAttr(_TagRunner):
    """
    Updates doc's attributes
    """


class TagDisplay(_TagRunner):
    """
    Run expression, display expression result
    """
    # stdout = None
    # value = None
    # return value, stdout, value


class TagShow(_TagRunner):
    """
    Display accumulated results
    """
