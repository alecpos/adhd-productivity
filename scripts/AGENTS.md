# Automation scripts guidelines

The `scripts/` directory houses maintenance and analytics utilities.

- Write Python automation scripts as single-entry modules with a `main()` function guarded by
  `if __name__ == "__main__":` to support importing.
- Shell scripts should be POSIX-compatible (`#!/usr/bin/env bash`) and use `set -euo pipefail` when
  mutating project state.
- Keep CLI interfaces consistent: prefer `argparse` with subcommands for Python and `getopts` for
  shell.
- Document new scripts in `scripts/README.md` with purpose, usage, and prerequisites.
- Place generated exports under `scripts/exports/` and ensure they are git-ignored when appropriate.
