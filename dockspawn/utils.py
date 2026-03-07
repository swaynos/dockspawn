import os
import re
import sys
import subprocess
from pathlib import Path

# Extract URL pattern like http://127.0.0.1:8889/lab?token=some_token
# or http://127.0.0.1:8889/?token=some_token
TOKEN_REGEX = re.compile(r"http://127\.0\.0\.1:(\d+)(\S*\?token=[^&\s]+)")

def get_run_dir(run_name: str) -> Path:
    """
    Resolve the run directory for a given run_name.
    It resolves to ~/.dockspawn/runs/<run_name>/
    """
    home = Path.home()
    return home / ".dockspawn" / "runs" / run_name

def run_command(cmd: list, cwd: Path = None, capture_output: bool = False, check: bool = True):
    """
    Wrapper around subprocess.run to execute a command and handle errors.
    """
    try:
        return subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=capture_output, 
            text=True, 
            check=check
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{' '.join(cmd)}' failed with exit code {e.returncode}.", file=sys.stderr)
        if e.stdout:
            print(f"Output:\n{e.stdout}", file=sys.stderr)
        if e.stderr:
            print(f"Error Output:\n{e.stderr}", file=sys.stderr)
        sys.exit(e.returncode)

def extract_jupyter_url(logs: str) -> str:
    """
    Given docker compose logs, extract the latest usable Jupyter URL.
    Returns None if no token is found.
    """
    latest_url = None
    for line in logs.splitlines():
        match = TOKEN_REGEX.search(line)
        if match:
            # Keep the last token URL seen so restarts don't return stale credentials.
            latest_url = match.group(0)
    return latest_url
