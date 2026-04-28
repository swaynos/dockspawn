import json
from pathlib import Path

from dockspawn.utils import get_run_dir

# Assuming templates are packaged alongside the module or installed via package_data
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def read_template() -> str:
    template_path = TEMPLATE_DIR / "docker-compose.yml"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found at {template_path}")
    return template_path.read_text()


def generate_run_directory(
    run_name: str,
    host_port: int,
    container_port: int,
    gpu_config: str,
    bind_ip: str = "127.0.0.1",
    workspace_dir: str = None,
):
    """
    Creates the ~/.dockspawn/runs/<name>/ directory and writes out:
    - docker-compose.yml (interpolated)
    - .env
    - run.json (metadata)
    """
    run_dir = get_run_dir(run_name)
    run_dir.mkdir(parents=True, exist_ok=True)

    if workspace_dir is None:
        workspace_dir = str(Path.home())

    env_vars = {
        "DOCKSPAWN_RUN_NAME": run_name,
        "DOCKSPAWN_HOST_PORT": str(host_port),
        "DOCKSPAWN_CONTAINER_PORT": str(container_port),
        "DOCKSPAWN_BIND_IP": bind_ip,
        "DOCKSPAWN_WORKSPACE": workspace_dir,
        "DOCKSPAWN_GPU_DEVICES": gpu_config if gpu_config else "all",
    }

    env_path = run_dir / ".env"
    with open(env_path, "w") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")

    # Keep compose parser happy with `gpus: all` and pin IDs via env var.
    gpu_section = ""
    if gpu_config:
        gpu_section = "\n    gpus: all"

    compose_path = run_dir / "docker-compose.yml"
    template_content = read_template()
    composed_content = template_content.format(
        DOCKSPAWN_RUN_NAME=run_name,
        DOCKSPAWN_BIND_IP=bind_ip,
        DOCKSPAWN_HOST_PORT=host_port,
        DOCKSPAWN_CONTAINER_PORT=container_port,
        DOCKSPAWN_WORKSPACE=workspace_dir,
        GPU_SECTION=gpu_section,
    )
    compose_path.write_text(composed_content)

    run_metadata = {
        "name": run_name,
        "host_port": host_port,
        "container_port": container_port,
        "gpu": gpu_config,
        "workspace": workspace_dir,
    }
    json_path = run_dir / "run.json"
    with open(json_path, "w") as f:
        json.dump(run_metadata, f, indent=2)

    return run_dir
