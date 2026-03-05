def parse_gpu_config(gpu_arg: str) -> str:
    """
    Parses a user-supplied GPU string into a valid Docker Compose deployment resource payload.
    If the arg is "all" or empty, returns "all".
    Otherwise, treats it as a comma-separated list of device IDs and returns a list in a string array format,
    e.g. "['0', '1']", because Compose requires a string or block sequence for device IDs.
    """
    if not gpu_arg or gpu_arg.lower() == "all":
        # In docker compose, 'count: all' handles assigning all GPUs
        return "all"
    
    # E.g. "0,1" -> "['0', '1']"
    parts = [p.strip() for p in gpu_arg.split(",") if p.strip()]
    
    # We return the raw string formatted as a YAML array because we template it directly
    formatted_list = ", ".join(f"'{p}'" for p in parts)
    return f"[{formatted_list}]"
