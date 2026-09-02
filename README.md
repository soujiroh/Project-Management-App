<<<<<<< HEAD
# Project-Management-App
=======
# Project Management App

This project is a Tkinter-based GUI application for simple project management.

Quick start (macOS)

1. Create a virtual environment using Python 3.13 (recommended):

```bash
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

2. Run the app:

```bash
python PMA.py
```

3. In VS Code: open the workspace and select the interpreter at `.venv/bin/python` (or the setting is preconfigured in `.vscode/settings.json`). Use the `Python: Launch (venv)` debug configuration to run.

If you prefer to run without a venv, run with the system Python that has Tk support:

```bash
/usr/bin/python3 "Project Management App_GRP2.py"
```

If you run into GUI visibility issues, start the app from Terminal (not detached debugger) and ensure the interpreter has `_tkinter` support.
>>>>>>> 14253ef (Initial commit: PMA rename, assets, UI updates, RoundedButton)
Notes
- If you run into GUI visibility issues on macOS, start the app from Terminal (not detached debugger) and ensure the interpreter has `_tkinter` support.
- The main script was renamed to `PMA.py` during refactor; adjust run/debug configurations accordingly.

Development
- The UI files are organized under `pm_app/` and assets in `assets/`.
- To push changes to GitHub, ensure your local branch is up-to-date with the remote, resolve any merge conflicts, and run `git push`.
