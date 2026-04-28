def parse_gpu_config(gpu_arg: str) -> str:
    """Normalize --gpu argument for compose runtime usage.

    Returns:
    - "all" for empty/all
    - "0", "1", "0,1" for specific devices
    """
    if not gpu_arg or gpu_arg.strip().lower() == "all":
        return "all"

    parts = [p.strip() for p in gpu_arg.split(",") if p.strip()]
    if not parts:
        return "all"

    return ",".join(parts)
