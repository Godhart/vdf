from pathlib import Path

import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def run(dut):
    """
    Runs simulation for certain time
    Drives and monitors signals
    """

    await Timer(100, units="ns")
