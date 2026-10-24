# Run the project on Windows

These steps set up and run the whole project on Windows 10 or 11 with PowerShell: tests, the
8-stage pipeline, the dashboard, the MLflow UI and the failure demonstrations. No Docker is needed.
The same steps are checked automatically on Windows in the project's GitHub Actions
(*Quality checks* runs on both Ubuntu and Windows).

## 1. Install the tools (once)

1. **Python 3.12** from https://www.python.org/downloads/windows/ (64-bit installer).
   On the first installer screen tick **"Add python.exe to PATH"**.
2. **Git for Windows** from https://git-scm.com/download/win (default options are fine).

Open a new **PowerShell** window and check both:

```powershell
py -3.12 --version
git --version
```

## 2. Get the code

```powershell
cd $HOME\Documents
git clone https://github.com/Swagata-Bhowmik/group4-mlflow-capstone.git
cd group4-mlflow-capstone
```

## 3. Create a virtual environment and install dependencies

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.lock
```

If PowerShell refuses to run `Activate.ps1` ("running scripts is disabled"), allow scripts for
your user once, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Your prompt now starts with `(.venv)`. Activate it again in every new PowerShell window.
Installing takes a few minutes the first time.

## 4. Run the tests

```powershell
python -m pytest -q
```

Expected: `16 passed`.

## 5. Run the pipeline

```powershell
python -m capstone run
```

This runs all eight stages (ingest, validate, features, train, evaluate, register, deploy,
monitor), trains the model, registers it in MLflow and deploys it locally. It prints one line per
stage and finally `RUN_DIRECTORY=...`. Results are written to `state\` and `reports\`.

## 6. Start the API and the dashboard

```powershell
python -m capstone serve
```

Leave this window open and visit:

- Dashboard: http://localhost:8000/
- API docs (try `POST /predict`): http://localhost:8000/docs
- Model lineage: http://localhost:8000/lineage

If Windows Firewall asks, choose **Private networks** only. Stop the server with `Ctrl + C`.

## 7. Open MLflow (run history and registry)

In a second PowerShell window, from the project folder:

```powershell
.\.venv\Scripts\Activate.ps1
mlflow ui --backend-store-uri sqlite:///state/mlflow.db --port 5000
```

Open http://localhost:5000. *Training runs* shows every run (failed ones too); *Models* →
`house-price-regressor` shows the `champion` alias and lifecycle tags.

## 8. Try the safety features

```powershell
# Bad data and a bad model are both rejected while a live server keeps answering
python scripts/live_safe_failure.py

# Re-run one stage of an existing run (use the RUN_DIRECTORY printed in step 5)
python -m capstone stage evaluate --run state\runs\<run-id>

# Drift and error report for the three incoming batches
python -m capstone monitor
```

Open `reports\monitoring.html` in a browser to see the batch report.

To see a gate stop a weak model, copy `config.yaml` to `my_config.yaml`, change
`quality: max_mae` to `5.0`, and run `python -m capstone --config my_config.yaml run --stop-after evaluate`.
The run fails at *evaluate* and the deployed model is unchanged.

## 9. Start again from scratch (optional)

```powershell
Remove-Item -Recurse -Force state -ErrorAction SilentlyContinue
python -m capstone run
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `py` is not recognised | Reinstall Python with "Add python.exe to PATH", or use `python` instead of `py -3.12` |
| `Activate.ps1` cannot be loaded | Run the `Set-ExecutionPolicy` command in step 3 |
| `pip install` fails on a package | Check you are on Python **3.12** (`python --version`) and inside `(.venv)` |
| Port 8000 or 5000 already in use | Close the other program, or for MLflow use `--port 5001` |
| Dashboard says "API unavailable" | Make sure `python -m capstone serve` is still running in its window |
| Errors mentioning old paths after moving the folder | Delete `state\` and run the pipeline again (step 9) |
