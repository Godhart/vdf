""" nbwavedrom - wavedrom timing diagrams for jupyter notebook """
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import IPython.display


def draw(data, png=False):
    """
    A function to provide digital waveform drawing in jupyter notebook.
    You need to have wavedrom-cli (https://github.com/wavedrom/cli) installed.

    Example usage:
        import nbwavedrom as wd
        wd.draw({
        'signal': [
          {'name': 'clk', 'wave': 'p.....|...'},
          {'name': 'dat', 'wave': 'x.345x|=.x', 'data': ['head', 'body', 'tail', 'data']},
          {'name': 'req', 'wave': '0.1..0|1.0'},
          {},
          {'name': 'ack', 'wave': '1.....|01.'}
        ]})

    The following arguments are used:
    * data - the wavedrom configuration (see wavedrom.com)
    """
    wavedrom_cli = shutil.which("wavedrom-cli")
    if wavedrom_cli is None:
        raise RuntimeError(
            "wavedrom-cli not found, visit https://github.com/wavedrom/cli for installation instructions"
        )

    if not isinstance(data, str):
        data = json.dumps(data)

    extra_args = []
    png_path = None
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as f:
        if png:
            png_path = f"{f.name}.png"
            extra_args += ["-p", png_path]

        f.write(data)
        f.flush()
        result = subprocess.run(
            [wavedrom_cli, "-i", f.name, *extra_args],
            encoding="utf-8",
            input=data,
            capture_output=True,
            check=True,
        )

        if png:
            with open(png_path, "rb") as f_png:
                result = f_png.read()
            Path(png_path).unlink()
        else:
            result = IPython.display.SVG(result.stdout)

    return result
