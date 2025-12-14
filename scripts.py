"""
Small npm-like script runner.
Usage:
  python scripts.py run <name> [-- ...args]
  python scripts.py <name> [-- ...args]

It loads `scripts.json` from the repository root and runs the mapped shell command.
Extra arguments after `--` are appended to the command.
"""
import json
import os
import shlex
import subprocess
import sys

ROOT = os.path.dirname(__file__)
SCRIPTS_FILE = os.path.join(ROOT, 'scripts.json')


def load_scripts():
    try:
        with open(SCRIPTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load scripts.json: {e}")
        return {}


def run_script(name, extra_args=None):
    scripts = load_scripts()
    cmd = scripts.get(name)
    if cmd is None:
        print(f"Script '{name}' not found in scripts.json")
        return 2

    # Append extra args if provided
    if extra_args:
        # If cmd is a string, append arguments safely
        cmd = cmd + ' ' + ' '.join(shlex.quote(a) for a in extra_args)

    print(f"Running: {cmd}")
    # Use shell to run complex commands exactly as in npm scripts
    proc = subprocess.run(cmd, shell=True)
    return proc.returncode


def print_usage():
    print(__doc__)


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print_usage()
        return 0

    # allow `run` subcommand like npm: `scripts.py run test`
    if argv[0] == 'run' and len(argv) >= 2:
        name = argv[1]
        rest = []
        if '--' in argv:
            idx = argv.index('--')
            rest = argv[idx+1:]
        return run_script(name, rest)

    # allow direct: `scripts.py test`
    name = argv[0]
    rest = []
    if '--' in argv:
        idx = argv.index('--')
        rest = argv[idx+1:]
    return run_script(name, rest)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
