## Current Plan to Fix CI Issues

This plan addresses the `ModuleNotFoundError` for `librosa`, `black` and `isort` formatting issues, and `flake8` code quality issues reported in the GitHub Actions CI.

### Step 1: Fix Dependencies (`pyproject.toml` and `poetry.lock`)
1.  Add `librosa = "^0.11.0"` and `psutil = "^7.0.0"` back to the `[tool.poetry.group.dev.dependencies]` section in `pyproject.toml`.
2.  Run `poetry lock` to update the `poetry.lock` file to reflect the changes in `pyproject.toml`.

### Step 2: Fix Code Formatting (using `black` and `isort`)
1.  Run `poetry run black .` to automatically reformat all Python files according to `black`'s style.
2.  Run `poetry run isort .` to automatically sort import statements in all Python files according to `isort`'s rules.

### Step 3: Fix Code Quality (`flake8` issues)
1.  Identify and remove the unused `global` statements in `whisper-dictation.py` as reported by `flake8` (e.g., `global last_heartbeat`, `global watchdog_active`, `global recording`, `global app`).

### Step 4: Commit and Push All Changes
1.  Stage all modified files: `pyproject.toml`, `poetry.lock`, and all `.py` files that were formatted or had `flake8` issues fixed.
2.  Commit the changes with a descriptive message.
3.  Push the commit to the remote repository.

This comprehensive approach will resolve all currently identified CI failures and ensure the pipeline runs smoothly with the new `continue-on-error` configurations.