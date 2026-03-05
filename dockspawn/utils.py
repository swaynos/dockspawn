import os
import re
import sys
import subprocess
from pathlib import Path

# Extract URL pattern like http://127.0.0.1:8889/lab?token=some_token
# or http://127.0.0.1:8889/?token=some_token
TOKEN_REGEX = re.compile(r'http://127\.0\.0\.1:(\d+)(\S*\?token=[a-zA-Z0-9]+)')

def get_run_dir(run_name: str) -> Path:
    """
    Resolve the run directory for a given run_name.
    It resolves to ~/.accelerator/runs/<run_name>/
    """
    home = Path.home()
    return home / ".accelerator" / "runs" / run_name

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
    Given docker compose logs, extract the first usable Jupyter URL.
    Returns None if no token is found.
    """
    for line in logs.splitlines():
        match = TOKEN_REGEX.search(line)
        if match:
            # We matched the URL! Note that the port in the logs might be 8888 (the container port).
            # The CLI up command needs to substitute the real host port, so returning the match object or raw token might be safer if we let the CLI format it.
            # But let's just return what matched first for simplicity, the CLI wrapper can format the final URL.
            return match.group(0)
    return None
