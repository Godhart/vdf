import time
import math
from pathlib import Path
from ..vdf.literals import *
from ..helpers import *
import re

import cocotb
from cocotb.triggers import Timer, RisingEdge, Edge, FallingEdge, ClockCycles, NextTimeStep
from cocotb.utils import get_sim_time, get_sim_steps


_TIME_SCALE = to_dict(
    fs = 1,
    ps = 1000,
    ns = 1000000,
    us = 1000000000,
    ms = 1000000000000,
    s  = 1000000000000000,
)
_FALLBACK_POLL_PERIOD = "10 ns"


@critical_todo
def _lookup_child(root, path:str|list[str], separator="."):
    """
    Lookup for nested child object by given hierarchical path
    """
    if isinstance(path, str):
        items = path.split(separator)
    else:
        items = path
    result = root
    for v in items:
        if hasattr(result, v):
            result = getattr(result, v)
        else:
            # TODO: Replace raise with cocotb's errors handling methods
            raise ValueError(f"Can't find element {v} for signal {'.'.join(items)}!")
    return result


def _to_time_steps(time_value: list[float,str]|dict|int|str) -> int:
    """
    Convert time into simulator's time steps
    """
    if isinstance(time_value, int):
        return int
    if isinstance(time_value, (list, tuple)) \
    and len(time_value) == 2 \
    and isinstance(time_value[0], (int, float)) \
    and time_value[1] in ("fs", "ps", "ns", "us", "ms", "s"):
        return get_sim_steps(*time_value)
    if isinstance(time_value, dict):
        return get_sim_steps(**time_value)
    if isinstance(time_value, str):
        parsed = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(fs|ps|ns|us|ms|s)\s*$", time_value)
        if parsed is not None:
            return _to_time_steps([float(parsed.groups()[0]), parsed.groups()[1]])
    raise ValueError(f"Don't know how to convert {time_value} into time steps!")


@critical_todo
async def run_sample(dut, data:dict, result:dict):
    """
    Task that will sample specified signals
    at necessary moments described as trigger
    """
    signals         = data[S_SIGNALS]
    trigger         = data[S_TRIGGER]
    trigger_options = data[S_TRIGGER_OPTIONS]

    if not isinstance(signals, (list, tuple)):
        signals = [signals]

    signals_map = {}
    for v in signals:
        if isinstance(v, str):
            v = v.split(".")
        signals_map[".".join(v)] = _lookup_child(dut, v)

    samples = []
    result[S_SAMPLES] = samples

    # print("Running sample")
    if trigger == S_TIME:
        for v in trigger_options:
            next_trigger = _to_time_steps(v)
            await Timer(next_trigger)
            values = {}
            sample = to_dict(time=f"{get_sim_time(units='ns')} ns",values=values)
            # print(f"  Sampling at {sample['time']}")
            for k,v in signals_map.items():
                values[k] = str(v.value)
                # print(f"    Sampled {k}={values[k]}")
            samples.append(sample)
    else:
        # TODO: Replace raise with cocotb's errors handling methods
        raise ValueError(f"Trigger kind '{trigger}' is not supported!")


_PROC_MAP = {
    S_SAMPLE : run_sample,
}


@cocotb.test()
async def run(dut):
    """
    Run simulation and specified tasks
    Save tasks results
    """

    runner_schedule_path = Path(f"./{C_RUNNER_SCHEDULE}")
    if runner_schedule_path.exists():
        runner_schedule = load_jyt(runner_schedule_path)
    else:
        runner_schedule = {}

    tasks_data = runner_schedule.get(S_TASKS, {})

    max_runtime = runner_schedule.get(S_MAX_RUNTIME, 30.)
    min_simtime = runner_schedule.get(S_MIN_SIMTIME, None)
    max_simtime = runner_schedule.get(S_MAX_SIMTIME, None)
    poll_period = runner_schedule.get(S_POLL_PERIOD, _FALLBACK_POLL_PERIOD)

    results = {C_EXCEPTION: []}
    tasks = {}
    try:
        if max_runtime < 1.:
            max_runtime = 1.
        if max_simtime is not None:
            max_simtime = _to_time_steps(max_simtime)
        if min_simtime is not None:
            min_simtime = _to_time_steps(min_simtime)
        poll_period = _to_time_steps(poll_period)

        for task_name, task_data in tasks_data.items():
            results[task_name] = {}
            kind = task_data.get(S_KIND, None)
            if kind is None:
                raise ValueError(f"No '{S_KIND}' is set for task '{task_name}'!")
            if kind not in _PROC_MAP:
                raise ValueError(f"Unsupported task kind '{kind}'!")
            print(f"Starting task {task_name}")
            tasks[task_name] = cocotb.start_soon(_PROC_MAP[kind](dut, task_data, results[task_name]))

        current_runtime = time.time()
        end_runtime = current_runtime + max_runtime
        any_running = len(tasks) > 0
        current_simtime = 0

        while current_runtime < end_runtime \
        and (max_simtime is None or current_simtime < max_simtime) \
        and (
                any_running
            or (min_simtime is not None and current_simtime < min_simtime)
        ):
            if False:   # TODO: turn on in test for max runtime
                # NOTE: code below is just to test how tasks are closed when max runtime is reached
                wait_time = min(math.floor(current_runtime) + 1.0, end_runtime) - current_runtime
                time.sleep(wait_time)
            await Timer(poll_period)
            any_running = any(v.done() is False for v in tasks.values())
            current_simtime = get_sim_time()
            current_runtime = time.time()

        any_running = any(v.done() is False for v in tasks.values())
        if any_running:
            results[C_EXCEPTION].append(str(f"Stopping prematurely since since max runtime {max_runtime} is reached!"))
            for k,v in tasks.items():
                if v.done() is False:
                    results[C_EXCEPTION].append(str(f"Stopping task {k}!"))
                    v.close()
            await Timer(poll_period)
        for k,v in tasks.items():
            if v.done() is False:
                results[C_EXCEPTION].append(str(f"Killing task {k}!"))
                v.kill()
        for k,v in tasks.items():
            try:
                v.result()
            except Exception as e:
                results[C_EXCEPTION].append(f"Exception in task '{k}': {e}")

    except Exception as e:
        results[C_EXCEPTION].append(str(e))

    save_jyt(results, Path(f"./{C_RUNNER_RESULTS}"))
