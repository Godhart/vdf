import inspect
from pathlib import Path
import os
import re
import toml
import ruamel.yaml
yaml = ruamel.yaml.YAML()
import json
import base64


_STRINGABLE = (Path, )

# Allow to run code that looks unsafe
_DEFAULT_UNSAFE_ALLOWED = "true"

# Allow to run with critical TODOs by default
_DEFAULT_CRITICAL_TODO_ALLOWED = "true"

# Allow to run with stub functions by default
_DEFAULT_STUB_ALLOWED = "true"

# Allow to run with non-implemented functions by default
# (but will break anyway if they are called)
_DEFAULT_NOT_IMPLEMENTED_ALLOWED = "true"


def any_to_dict_list_scalar(
        inst,
        instance_map=None,
        lists_as_tuple=True
):
    """
    Translate any object's instance (fields) and it's content recursively
    into dict/list/scalar as much as it's possible
    """
    if instance_map is None:
        instance_map = {}
    result = None
    if inst is None:
        pass
    elif isinstance(inst, (str, int, float, bool, )):
        result = inst
    elif inspect.isclass(inst):
        result = str(inst)
    elif isinstance(inst, _STRINGABLE):
        result = str(inst)
    elif isinstance(inst, dict) or (
            hasattr(inst, "items")  and callable(getattr(inst, "items"))
        and hasattr(inst, "keys")   and callable(getattr(inst, "keys"))
        and hasattr(inst, "values") and callable(getattr(inst, "values"))
    ):
        result = {}
        for k,v in inst.items():
            result[any_to_dict_list_scalar(k, instance_map, lists_as_tuple)] = \
                any_to_dict_list_scalar(v, instance_map, lists_as_tuple)
    elif hasattr(inst, "to_dict") and callable(getattr(inst, "to_dict")):
        if inst in instance_map:
            result = instance_map[inst]
        else:
            result = {}
            instance_map[inst] = result
            for k,v in inst.to_dict().items():
                result[k] = v
    elif isinstance(inst, (list, tuple)) or hasattr(inst, "__iter__"):
        result = []
        for v in inst:
            result.append(any_to_dict_list_scalar(v, instance_map, lists_as_tuple))
        if lists_as_tuple:
            result = tuple(result)
    elif " object at" not in str(inst):
        if inst in instance_map:
            result = instance_map[inst]
        else:
            instance_map[inst] = result
            result = str(inst)
    else:
        if inst in instance_map:
            result = instance_map[inst]
        else:
            result = {}
            instance_map[inst] = result
            for k in dir(inst):
                if k[:1] == "_":
                    continue
                v = getattr(inst, k)
                if callable(v) and inspect.isclass(v) is False:
                    continue
                result[k] = any_to_dict_list_scalar(v, instance_map, lists_as_tuple)
    if isinstance(result, dict):
        tmp = {}
        for k,v in sorted(result.items(), key=lambda x: str(x[0])):
            if not isinstance(k, (str, int, )):
                k = str(k)
            tmp[k] = v
        result = tmp
    return result


def to_dict(**kwargs):
    """
    Returns dict, constructed from kwargs
    """
    return {**kwargs}


class EzClass:
    """
    Produce class with fields that are kwargs' keys
    """
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            if not isinstance(k, str):
                raise ValueError(f"Got non-string key: {k}!")
            if re.match(r"^[a-zA-Z_]\w*$", k) is None:
                raise ValueError(
                    f"Bad error for key: {k}!"
                    " Start with alpha or underscore,"
                    " continue with alpha_numerics")
            setattr(self, k, v)


def unsafe(f):
    """
    Decorator allows run function with unsafe code parts
    if VDF_UNSAFE_ALLOWED is set
    """
    if not os.environ.get(
        "VDF_CRITICAL_TODO_ALLOWED",
        _DEFAULT_UNSAFE_ALLOWED).lower() in ("1", "true", "yes"
    ):
        raise NotImplementedError(
            f"There is unsafe code in function '{f.__name__}'!"
            " Implement properly before going to prod!"
        )
    def wrapped(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapped


def critical_todo(f):
    """
    Decorator allows run function with critical TODOs
    if VDF_CRITICAL_TODO_ALLOWED is set
    """
    if not os.environ.get(
        "VDF_CRITICAL_TODO_ALLOWED",
        _DEFAULT_CRITICAL_TODO_ALLOWED).lower() in ("1", "true", "yes"
    ):
        raise NotImplementedError(
            f"There is critical TODOs left in function '{f.__name__}'!"
            " Implement properly before going to prod!"
        )
    def wrapped(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapped


def stub_alert(f):
    """
    Decorator allows run subbed function
    if VDF_STUB_ALLOWED is set
    """
    if not os.environ.get(
        "VDF_STUB_ALLOWED",
        _DEFAULT_STUB_ALLOWED).lower() in ("1", "true", "yes"
    ):
        raise NotImplementedError(
            f"Function '{f.__name__}' is a stub! Implement properly before going to prod!"
        )
    def wrapped(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapped


def not_implemented(f):
    """
    Decorator allows compile function but not run
    if VDF_NOT_IMPLEMENTED_ALLOWED is set
    """
    if not os.environ.get(
        "VDF_NOT_IMPLEMENTED_ALLOWED",
        _DEFAULT_NOT_IMPLEMENTED_ALLOWED).lower() in ("1", "true", "yes"
    ):
        raise NotImplementedError(f"Function '{f.__name__}' is not implemented at all!")
    def wrapped(*args, **kwargs):
        # Fail anyway
        def ff(*args, **kwargs):
            raise NotImplementedError(f"Function '{f.__name__}' is not implemented at all!")
        return ff(*args, **kwargs)
    return wrapped


def replace_escaped(
        line:str,
        replacement_char:str,
        escape_symbol:str="\\"
    ) -> str:
    """
    Replaces escaped chars in line with replacement_char
    """
    if escape_symbol is None:
        return line
    result = ""
    prev = None
    for char in line:
        if prev == escape_symbol:
            result += replacement_char
            prev = replacement_char
        else:
            result += char
            prev = char
    return result


def load_jyt(path: str) -> dict:
    """
    Load data from JSON / YAML / TOML file
    If data in file is not a dict then dict is created
    with '__root__' (C_ROOT) as key and loaded data as value
    """
    with open(path, "rb") as f:
        sfx = Path(path).suffix
        if sfx in (".yaml", ".yml"):
            data = yaml.load(f)
        elif sfx in (".toml", ):
            data = toml.loads(f.read().decode())
        elif sfx in (".json", ):
            data = json.loads(f.read().decode())
        else:
            raise ValueError(
                f"Unknown file format (extension '{sfx}')!"
                " Use '.json', '.yaml', '.yml' or '.toml'")
    if not isinstance(data, dict):
        data = to_dict(__root__ = data)
    return data

def save_jyt(data, path: str):
    """
    Save data to JSON / YAML / TOML file
    """
    sfx = Path(path).suffix
    if sfx not in (".yaml", ".yml", ".toml", ".json", ):
        raise ValueError(
            f"Unknown file format (extension '{sfx}')!"
            " Use '.json', '.yaml', '.yml' or '.toml'")

    with open(path, "w") as f:
        sfx = Path(path).suffix
        if sfx in (".yaml", ".yml"):
            yaml.dump(data, f)
        elif sfx in (".toml", ):
            toml.dump(data, f)
        elif sfx in (".json", ):
            data = json.dump(data, f, indent=2)

def markdown_png(text: str, data:bytes) -> str:
    d64 = base64.b64encode(data).decode()
    return f"![{text}](data:image/png;base64,{d64})"
