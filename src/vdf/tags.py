from pathlib import Path
from copy import deepcopy
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
        # TODO: mandatory flag
        # TODO: format
        # TODO: check against format when value is applied


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
            name      : str,
            kind      : str,
            runner    : str,    # TODO: |callable into typehint,
            vars      : dict,
            subtags   : dict,
            args      : list[dict],
            value     : str|None,
            output    : list[str],
            accumulate: bool,
            requires  : list[str],
        ):
        self.name = name
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

        self.value = value

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
    def __init__(
            self,
            tagdef: TagDef,
            line:str,
            subtag:str,
            vars:dict,
            args:list[str],
            value
        ):
        self._tagdef = tagdef
        self.line = line
        self.subtag = subtag
        self.vars = vars
        self.args = args
        self.value = value

    @property
    def tagdef_name(self):
        return self._tagdef.name

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
        data[tagdef] = TagDef(name=tagdef,**data[tagdef])
    del data[S_FALLBACK]
    result = TagDefs(data)
    return result


TAG_DEFS = load_tags(Path(__file__).parent / "tags.yaml")


def _apply_tag_var(tag_def:TagDef, vars, name, value, line):
    if name not in tag_def.vars:
        raise ValueError(
            f"Variable with name '{name}' is not specified for tag!"
            f" (line '{line}')")
    if name not in vars:
        vars[name] = TagVar(name, value)
    else:
        raise ValueError(
            f"Variable '{name}' is already defined for tag!"
            f" (line '{line}')")


@critical_todo
def parse_tag(line:str) -> TagInstance:
    """
    Parse line with tag data into tag instance, do basic validation
    """
    # Split line into items
    items = line.split("-") # TODO: avoid escaped -

    # Lookup joined items in tag defs while not found
    # with each unsuccessful try drop rightmost item
    tag_items=items
    while len(tag_items) > 0 and "-".join(tag_items) not in TAG_DEFS.tags:
        tag_items = tag_items[:-1]
    if len(tag_items) == 0:
        raise ValueError(f"Not found any tag definition for '{line}'!")
    tag_data = items[len(tag_items):]

    # General tag instance data initialization
    tag_name = "-".join(tag_items)
    tag_def = TAG_DEFS.tags[tag_name]
    tag_vars = {}
    tag_subtag = None
    tag_args = []
    tag_value = None

    # Get specs for vars and args
    # NOTE: don't mess up def's data, so do deepcopy
    tag_vars_spec = deepcopy(tag_def.vars)
    tag_args_spec = deepcopy(tag_def.args)

    # Process rest tag data:
    # 1. subtag
    # 2. args
    # 3. value

    # Look for subtag, update vars if found
    if len(tag_def.subtags) > 0:
        subtags_items = tag_data
        while len(subtags_items) > 0 \
                and "-".join(subtags_items) not in tag_def.subtags:
            subtags_items = subtags_items[:-1]
        tag_data = tag_data[len(subtags_items):]
        if len(subtags_items) > 0:
            tag_subtag = "-".join(subtags_items)
            for _,v in tag_def.subtags[tag_subtag].vars.items():
                _apply_tag_var(tag_def, tag_vars, v.name, v.value, line)
                # TODO: change tag_args_spec
                # remove args that are setting vars that were set already

    # Look for args
    kw_part = False # True if keyworded part started
    arg_idx = 0
    run_once = True
    while len(tag_args_spec) > 0 or kw_part or run_once:
        run_once = False
        # Get value for arg
        if len(tag_data) > 0:
            arg_value = tag_data[0]
            tag_data = tag_data[1:]
        else:
            arg_value = None

        if arg_value == "":
            # NOTE: if empty value is received that means it's end of args
            if len(tag_data) > 0:
                if tag_def.value is None:
                    raise ValueError(
                        f"Value is specified but it's not supported in '{line}'!")
                tmp = "-".join(tag_data)
                tag_data = []
                # TODO: check tag_value format
                tag_value = tmp
            break

        if arg_value is None and kw_part:
            break

        if arg_value is not None:
            if ":" in arg_value:
                kw_part = True
            else:
                if kw_part:
                    raise ValueError(
                        f"Got raw value '{arg_value}' when '<name>:<value>'"
                        f" is expected in '{line}'!"
                    )

        if kw_part:
            var_name, var_value = arg_value.split(":",1)
            _apply_tag_var(tag_def, tag_vars, var_name, var_value, line)
            continue

        # Get arg spec
        if len(tag_args_spec) == 0:
            break
        arg_spec = tag_args_spec[0]
        tag_args_spec = tag_args_spec[1:]
        arg_idx += 1

        if arg_value is None:
            if arg_spec.mandatory:
                raise ValueError(
                    f"Mandatory arg #{arg_idx} is not specified in '{line}'!")
            else:
                break

        format_ok = True
        # TODO: check arg_value against required format

        if format_ok:
            _apply_tag_var(tag_def, tag_vars, arg_spec.var_name, arg_value, line)
            tag_args.append(arg_value)
        else:
            if arg_spec.mandatory:
                raise ValueError(
                    f"Format error for arg #{arg_idx} in '{line}'!")
            else:
                # Try luck with next arg, so put arg_value back to tag_data
                tag_data = [arg_value] + tag_data

    # Make sure no non-processed data is left
    if len(tag_data) > 0:
        raise ValueError(
            f"Extra args or format error"
            f" for optional args in line '{line}'!\n"
            f"Extra part is '{'-'.join(tag_data)}'")

    # Make sure value is set if it's mandatory
    if tag_def.value is not None \
            and tag_def.value[:1] != "?" \
            and tag_value is None:
        raise ValueError(
            f"No value is set in line '{line}'!"
        )

    for _, v in tag_def.vars.items():
        # TODO: make sure mandatory vars are set
        if v.name not in tag_vars:
            tag_vars[v.name] = TagVar(v.name, v.value)

    result = TagInstance(
        tag_def,
        line,
        tag_subtag,
        tag_vars,
        tag_args,
        tag_value
    )
    return result


@critical_todo
def parse_tags(lines:list[str]) -> TagsInstances:
    """
    Get tags out of magic line, create tags instance, check basic rules
    """
    result = TagsInstances([])
    if len(lines) < 1:
        return result

    # First - join multi lines if there is any
    # TODO: if source already have joined multi lines - don't do this, just use first line
    magic_line = "\\"
    i = -1
    while replace_escaped(magic_line, "_")[-1:] == "\\":
        i+=1
        if i == len(lines):
            raise ValueError("Not terminated multiline magic!")
        magic_line = magic_line[:-1] + lines[i]

    if magic_line[:len(S_VDF_PREAMBLE)] == S_VDF_PREAMBLE:
        magic_line = magic_line[len(S_VDF_PREAMBLE):]

    i = -1
    stack = None
    magic_line_e = replace_escaped(magic_line, "_")
    prev_char_e = None
    while i < len(magic_line)-1:
        i += 1
        char   = magic_line[i]
        char_e = magic_line_e[i]

        if char_e == "#" and (prev_char_e == " " or prev_char_e is None):
            if stack is not None:
                result.tags.append(parse_tag(stack[1:].rstrip()))
            stack = ""

        prev_char_e = char_e
        if stack is None:
            continue
        stack += char

    if stack is not None:
        result.tags.append(parse_tag(stack[1:].rstrip()))

    return result


@stub_alert
def get_name(tags: list[TagsInstances]|None) -> str|None:
    return None


@stub_alert
def get_parent(tags: list[TagsInstances]|None) -> str|None:
    return None
