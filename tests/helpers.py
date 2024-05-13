import os
import shutil
from pathlib import Path
import filecmp
import glob


def init_test_paths(file_location, test_set) -> tuple[str,str,str]:
    input_path  = Path(file_location).parent / "test" / test_set
    gold_path   = Path(file_location).parent / "gold" / test_set
    output_path = Path(file_location).parent / ".out" / test_set
    if output_path.exists():
        shutil.rmtree(output_path)
    os.makedirs(output_path)
    return input_path, gold_path, output_path


def same_as_gold(gold_path:str|Path, results_path:str|Path, ignore=None) -> bool:
    ignore_list = []
    ignore = ignore or []
    results_path = Path(results_path)
    for pattern in ignore:
        ignore_list += [
            str(Path(v).relative_to(results_path))
            for v in glob.glob(os.path.join(results_path, pattern))
        ]

    cmp = filecmp.dircmp(gold_path, results_path, ignore_list)
    return (
            len(cmp.left_only)
        +   len([v for v in cmp.right_only if v not in ignore_list])
        +   len(cmp.diff_files)
        +   len(cmp.funny_files)
        ) == 0 and (
            len(cmp.left_list) > 0       # Make sure there is gold data at all
        ) and (
            len(cmp.right_list) > 0      # Double check if path are swapped
        )


def copy_tree(src:str|Path, dst:str|Path, dirs_exist_ok=False, hidden=True):
    dst = Path(dst)
    for root, dirs, files in os.walk(src):
        root = Path(root)
        for f in files:
            if hidden is False and f[:1] == ".":
                continue
            shutil.copy2(root / f, dst / f)
        for d in dirs:
            os.makedirs(dst / d, exist_ok=dirs_exist_ok)
            copy_tree(root / d, dst / d, dirs_exist_ok, hidden)
        break


def list_tests(test_file_location:str|Path, folders:list[str]) -> list[str]:
    tests = []
    for f in folders:
        for root, dirs, _ in os.walk(Path(test_file_location).parent / f):
            for d in dirs:
                if (Path(root) / d / ".skip").exists():
                    continue
                tests.append(d)
            break
    tests = list(set(tests))
    return tests
