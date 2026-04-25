# dockspawn

Spin up disposable GPU-accelerated JupyterLab environments locally using Docker Compose.

dockspawn generates Docker Compose configurations and can optionally run them for you. It is designed for local GPU labs where you want a quick Jupyter environment without building extra infrastructure.

## Features

- Compose-first: relies on Docker Compose for lifecycle
- Automatically picks the next available host port starting at 8888
- Mounts your home directory into the container for read-write access
- Supports multi-GPU selection (default: all)
- Extracts the Jupyter token from logs and prints a clickable URL
- Minimal dependencies (prefer Python standard library)

## Requirements

- Docker
- Docker Compose
- NVIDIA Container Toolkit (for GPU support)

## Setup and Quick Start

1. **Install the package locally**:

   ```bash
   pip install .
   ```
   *(Tip: Use `pip install -e .` if you plan on modifying the code.)*

2. **Start a new environment**:

   ```bash
   dockspawn start
   ```

   **Example output:**
   ```text
   Environment ready
   http://127.0.0.1:8888/lab?token=<token>
   ```

## Defaults

### Ports

- Container: 8888
- Host: first available starting at 8888
- Bind address: 127.0.0.1 (use `--bind-ip 0.0.0.0` for external network access)

### Workspace

- Mount: $HOME -> /home/host
- Jupyter starts in: /home/host
- Run config lives in: `~/.dockspawn/runs/<name>`

### GPU

Default: all GPUs

Restrict GPU usage:

  dockspawn start --gpu 0
  dockspawn start --gpu 1
  dockspawn start --gpu 0,1

Allow external subnet access:

  dockspawn start --bind-ip 0.0.0.0

## Commands

- dockspawn gen   Generate compose files for a run
- dockspawn up    Start a generated run (docker compose up -d)
- dockspawn down  Stop a run (docker compose down)
- dockspawn logs  View logs for a run
- dockspawn start Convenience: gen + up + token extraction

## Philosophy

dockspawn intentionally avoids complexity.

It does not replace Docker or Docker Compose. It generates straightforward Compose configs and provides a small CLI to make local GPU Jupyter environments easy to launch and manage.

## License

GPL-3.0 
