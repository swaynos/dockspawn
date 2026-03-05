import argparse
import sys
import time
from pathlib import Path

from dockspawn.ports import get_next_available_port
from dockspawn.gpu import parse_gpu_config
from dockspawn.compose import generate_run_directory
from dockspawn.utils import get_run_dir, run_command, extract_jupyter_url

def cmd_gen(args):
    """Generate configuration for a run."""
    run_name = args.name
    run_dir = get_run_dir(run_name)
    
    if run_dir.exists() and not args.force:
        print(f"Error: Run directory already exists at {run_dir}")
        print("Use --force to overwrite, or choose a different name.")
        sys.exit(1)
        
    print(f"Generating run '{run_name}'...")
    
    gpu_config = parse_gpu_config(args.gpu)
    
    try:
        host_port = get_next_available_port(start_port=args.port)
    except RuntimeError as e:
        print(f"Error finding port: {e}", file=sys.stderr)
        sys.exit(1)
        
    generate_run_directory(
        run_name=run_name,
        host_port=host_port,
        container_port=8888,
        gpu_config=gpu_config,
        bind_ip="127.0.0.1",
        workspace_dir=args.workspace or str(Path.home())
    )
    
    print(f"Run directory created at: {run_dir}")
    print(f"Host port allocated: {host_port}")

def _ensure_run_exists(run_name: str) -> Path:
    run_dir = get_run_dir(run_name)
    if not run_dir.exists():
        print(f"Error: Run '{run_name}' not found at {run_dir}.", file=sys.stderr)
        print("Have you run 'dockspawn gen' first?", file=sys.stderr)
        sys.exit(1)
    return run_dir

def cmd_up(args):
    """Start a generated run."""
    run_dir = _ensure_run_exists(args.name)
    print(f"Starting run '{args.name}'...")
    run_command(["docker", "compose", "up", "-d"], cwd=run_dir)
    print("Environment is starting.")

def cmd_down(args):
    """Stop and remove a run's containers."""
    run_dir = _ensure_run_exists(args.name)
    print(f"Stopping run '{args.name}'...")
    run_command(["docker", "compose", "down"], cwd=run_dir)
    print("Environment stopped.")

def cmd_logs(args):
    """View logs for a run."""
    run_dir = _ensure_run_exists(args.name)
    cmd = ["docker", "compose", "logs"]
    if args.f:
        cmd.append("-f")
    # Subprocess run might consume the UI if -f is used, so we use replace standard run_command
    # for a streaming version if needed, or simply let it inherit stdout.
    try:
        # Since we want to stream output natively
        import subprocess
        subprocess.run(cmd, cwd=run_dir, check=True)
    except KeyboardInterrupt:
        pass
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

def cmd_start(args):
    """Convenience: gen + up + get token URL."""
    # 1. Gen
    # Default behavior of start is to force overwrite if it's an ephemeral run
    # For now, let's just bypass gen checks by treating it as a fresh generation
    args.force = True
    cmd_gen(args)
    
    # 2. Up
    run_dir = get_run_dir(args.name)
    print(f"Starting run '{args.name}'...")
    run_command(["docker", "compose", "up", "-d"], cwd=run_dir)
    
    # 3. Read json to get host port so we can format the final URL
    import json
    with open(run_dir / "run.json", "r") as f:
        metadata = json.load(f)
    host_port = metadata["host_port"]
    
    # 4. Extract token
    print("Waiting for Jupyter to start and expose token...")
    max_retries = 15
    url = None
    
    for _ in range(max_retries):
        time.sleep(2)
        res = run_command(["docker", "compose", "logs", "jupyter"], cwd=run_dir, capture_output=True)
        url = extract_jupyter_url(res.stdout or res.stderr)
        if url:
            break
            
    if url:
        # The URL extracted from logs might have container port 8888. Replace it with host_port.
        import re
        # Pattern captures port into group 1, remainder into group 2
        final_url = re.sub(r'(http://127\.0\.0\.1:)(\d+)(/.*)', rf'\g<1>{host_port}\g<3>', url)
        print("\nEnvironment ready")
        print(final_url)
    else:
        print("\nTimeout waiting for Jupyter token.", file=sys.stderr)
        print(f"Check logs with: dockspawn logs {args.name}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Spin up disposable GPU-accelerated JupyterLab environments.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # gen
    parser_gen = subparsers.add_parser("gen", help="Generate compose files for a run")
    parser_gen.add_argument("name", help="Name of the run")
    parser_gen.add_argument("--gpu", default="all", help="GPU config (e.g. 'all', '0', '0,1')")
    parser_gen.add_argument("--port", type=int, default=8888, help="Starting port to search for available host port")
    parser_gen.add_argument("--workspace", help="Workspace directory to mount (default: $HOME)")
    parser_gen.add_argument("--force", action="store_true", help="Overwrite existing run directory if it exists")
    
    # up
    parser_up = subparsers.add_parser("up", help="Start a generated run")
    parser_up.add_argument("name", help="Name of the run")
    
    # down
    parser_down = subparsers.add_parser("down", help="Stop a run")
    parser_down.add_argument("name", help="Name of the run")
    
    # logs
    parser_logs = subparsers.add_parser("logs", help="View logs for a run")
    parser_logs.add_argument("name", help="Name of the run")
    parser_logs.add_argument("-f", action="store_true", help="Follow log output")

    # start
    parser_start = subparsers.add_parser("start", help="Convenience: gen + up + token extraction")
    parser_start.add_argument("name", help="Name of the run (default: default)", nargs="?", default="default")
    parser_start.add_argument("--gpu", default="all", help="GPU config (e.g. 'all', '0', '0,1')")
    parser_start.add_argument("--port", type=int, default=8888, help="Starting port to search for available host port")
    parser_start.add_argument("--workspace", help="Workspace directory to mount (default: $HOME)")

    args = parser.parse_args()

    if args.command == "gen":
        cmd_gen(args)
    elif args.command == "up":
        cmd_up(args)
    elif args.command == "down":
        cmd_down(args)
    elif args.command == "logs":
        cmd_logs(args)
    elif args.command == "start":
        cmd_start(args)

if __name__ == "__main__":
    main()
