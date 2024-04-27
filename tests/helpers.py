import os
import shutil
from pathlib import Path
import filecmp


def init_test_paths(file_location, test_set):
    input_path  = Path(file_location).parent / "test" / test_set
    gold_path   = Path(file_location).parent / "gold" / test_set
    output_path = Path(file_location).parent / ".out" / test_set
    if output_path.exists():
        shutil.rmtree(output_path)
    os.makedirs(output_path)
    return input_path, gold_path, output_path


def same_as_gold(gold_path, results_path):
    cmp = filecmp.dircmp(gold_path, results_path)
    return (
            len(cmp.left_only)
        +   len(cmp.right_only)
        +   len(cmp.diff_files)
        +   len(cmp.funny_files)
        ) == 0 and (
            len(cmp.left_list) > 0       # Make sure there is gold data at all
        ) and (
            len(cmp.right_list) > 0      # Double check if path are swapped
        )


def copy_tree(src, dst, dirs_exist_ok=False, hidden=True):
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
    
    
def list_tests(test_file_location, folders):
    tests = []
    for f in folders:
        tests += os.listdir(Path(test_file_location).parent / f)
    tests = list(set(tests))
    return tests
