# Project Mission

This repository implements a lightweight CLI tool for launching GPU-accelerated JupyterLab environments locally using Docker Compose.

The tool generates Docker Compose configurations and can optionally run them for the user. It intentionally relies on Docker and Docker Compose rather than re-implementing container orchestration logic.

Primary goals:
- Fast GPU notebook environments
- Simple reproducible Compose configurations
- Minimal operational complexity
- Safe defaults for local development
- Very small dependency footprint

The project should remain easy to reason about and easy to debug.

---

# Guiding Principles

When modifying this repository:

1. Prefer simple implementations over complex abstractions.
2. Be selective about new dependencies. Prefer the Python standard library.
3. Do not re-implement functionality already provided by Docker or Docker Compose.
4. Make small, focused changes. Avoid refactoring unrelated code.
5. Favor clarity and maintainability over clever solutions.

---

# How the Project Works

This project is not a container runtime manager.

It is a Compose generator and helper CLI.

Typical flow:

1) Resolve configuration (defaults + CLI flags)
2) Generate a run directory containing:
   - docker-compose.yml
   - .env
   - run.json (metadata)
3) Optionally run:
   - docker compose up -d
4) Retrieve the Jupyter token from:
   - docker compose logs
5) Print a usable Jupyter URL

Docker Compose remains the source of truth for container lifecycle.

---

# Defaults

## Ports

- Jupyter runs inside the container on port 8888.
- The tool selects the first available host port starting at 8888 (8888, then 8889, then 8890, ...).
- Services bind to localhost only by default:

  127.0.0.1:<host_port>:8888

## Workspace

- Default mount: $HOME -> /home/host
- Default working directory: /home/host
- The container has read-write access to the mounted home directory.

## GPU Selection

- Default: all GPUs
- User may restrict GPUs:

  --gpu 0
  --gpu 1
  --gpu 0,1

## Token Handling

- Jupyter generates its own token.
- The tool extracts the first usable URL containing '?token=' from docker compose logs.
- The URL is printed to the user.

---

# Repository Structure

Suggested layout:

dockspawn/
  cli.py        # CLI parsing and command routing
  compose.py    # Compose generation and run directory writing
  ports.py      # Host port selection
  gpu.py        # GPU flag parsing and Compose GPU settings
  utils.py      # Small helpers (paths, subprocess, log parsing)

templates/
  docker-compose.yml

tests/

AGENTS.md
README.md

---

# Run Directories

Each run creates a directory:

  ~/.dockspawn/runs/<name>/

Example:

  ~/.dockspawn/runs/lab-123/
    docker-compose.yml
    .env
    run.json

This enables multiple independent environments.

---

# Commands

The CLI should support:

- dockspawn gen   (generate files only)
- dockspawn up    (docker compose up -d for a run)
- dockspawn down  (docker compose down for a run)
- dockspawn logs  (show logs for a run)
- dockspawn start (gen + up + token extraction + print URL)

---

# Security Requirements

- Bind to 127.0.0.1 by default.
- Do not expose services publicly by default.
- Do not disable authentication.

---

# Definition of Done

A change is complete when:

1. The CLI generates a valid Compose configuration.
2. docker compose up brings the environment online.
3. The tool can retrieve and print a working Jupyter URL.
4. Defaults remain simple and safe.
5. Dependency additions are justified and minimal.
