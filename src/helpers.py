import inspect


def any_to_dict_list_scalar(inst, instance_map=None, lists_as_tuple=True):
    if instance_map is None:
        instance_map = {}
    result = None
    if inst is None:
        pass
    elif isinstance(inst, (str, int, float, bool, )):
        result = inst
    elif inspect.isclass(inst):
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
        for k,v in result.items():
            if not isinstance(k, (str, int, )):
                k = str(k)
            tmp[k] = v
        result = tmp
    return result
