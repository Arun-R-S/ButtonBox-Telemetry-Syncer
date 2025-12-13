Running tests

Options to run tests:

1) Run with an HTML report (single command you provided):

```powershell
python -m pytest tests -q --html=report.html --self-contained-html
```

This produces `report.html` in the project root (self-contained, open in a browser).

2) (Optional) Create a virtual environment and install test deps:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

3) Run tests without a venv (per-user install):

```powershell
python -m pip install --user -r requirements.txt
python -m pytest tests -q
```

Notes:

Open report automatically
-------------------------

If you want the HTML report to open automatically after tests finish, use one of these commands.

PowerShell (always open):

```powershell
python -m pytest tests -q --html=report.html --self-contained-html; Start-Process report.html
```

PowerShell (open only on success):

```powershell
python -m pytest tests -q --html=report.html --self-contained-html
if ($LASTEXITCODE -eq 0) { Start-Process report.html }
```

Windows CMD (open only on success):

```cmd
python -m pytest tests -q --html=report.html --self-contained-html && start report.html
```

Cross-platform (use Python webbrowser):

```bash
python -m pytest tests -q --html=report.html --self-contained-html; python -m webbrowser report.html
```
