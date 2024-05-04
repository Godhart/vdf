from pathlib import Path
import yaml
from .literals import *
from ..helpers import *


_RUNNERS        = []


class TagVar:
    """
    Class for tag var definition
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value


class TagArg:
    """
    Class for tag argument definition
    """
    def __init__(self, var_name, mandatory, format,):
        self.var_name = var_name
        self.mandatory = mandatory
        self.format = format


class SubTag:
    """
    Class for subtag definition
    """
    def __init__(self, vars:dict):
        self.vars = {}
        for k,v in vars.items():
            self.vars[k] = TagVar(k, v)


class TagDef:
    """
    Class for tag definition
    """

    def __init__(
            self,
            kind      : str,
            runner    : str,    # TODO: |callable into typehint,
            vars      : dict,
            subtags   : dict,
            args      : list[dict],
            output    : list[str],
            accumulate: bool,
            requires  : list[str],
        ):
        self.kind = kind

        if isinstance(runner, str):
            if runner[:1] == "_":
                raise ValueError(f"Can use only public methods / classes, got '{runner}'!")
            runner_obj = None
            for v in _RUNNERS:
                if hasattr(v, runner):
                    runner_obj = getattr(v, runner)
            if runner_obj is None:
                raise ValueError(f"Runner with name '{runner}' wan't found within tags runners!")
            runner = runner_obj
        self.runner = runner

        self.vars = {}
        for k,v in vars.items():
            self.vars[k] = TagVar(k, v)

        self.subtags = subtags
        for k,v in subtags.items():
            self.subtags[k] = SubTag(**v)

        self.args = []
        for v in args:
            self.args.append(TagArg(**v))

        self.output = [*output]
        self.accumulate = accumulate
        self.requires = requires

    def match(self, line, offs) -> int:
        """
        Check if tag definition matches data in line (starting from offs)
        Return length of matched chars. 0 if not matched
        """

    def parse(self, line, offs, length):
        """
        Parse line (starting from offs and with specified length) and return TagInstance
        """


class TagDefs:
    """
    Class for tags defs consolidation
    """
    def __init__(self, tags: dict[str:TagDef]):
        self.tags = tags


class TagInstance:
    """
    Class for tag instance representation
    """
    def __init__(self, cell, tagdef: TagDef, vars):
        self.cell = cell
        self.tagdef = tagdef
        self.vars = vars


class TagsInstances:
    """
    Class for tags instances consolidation
    """
    def __init__(self, tags: list[TagInstance]):
        self.tags = tags


# NOTE: import and _RUNNERS redefined here due to circular references troubles
from . import tags_runners
_RUNNERS.append(tags_runners)


# NOTE: load tags here since classes are defined above
@unsafe
def load_tags(path):
    with open(path, "rb") as f:
        data = yaml.safe_load(f)
    for k,v in data[S_FALLBACK].items():
        for tagdef in data:
            if tagdef == S_FALLBACK:
                continue
            if tagdef[:1] == "_":
                raise ValueError(f"Tag name shouldn't start with '_' (tag name = '{tagdef}')")
            if k not in data[tagdef]:
                data[tagdef][k] = v
    # TODO: more sanity/safety checks
    for tagdef in data:
        if tagdef == S_FALLBACK:
            continue
        data[tagdef] = TagDef(**data[tagdef])
    del data[S_FALLBACK]
    result = TagDefs(data)
    return result


TAG_DEFS = load_tags(Path(__file__).parent / "tags.yaml")


@stub_alert
def parse_tags(lines:list[str]) -> tuple[list[TagsInstances], str, str]:
    return [], None, None
