import socket

def get_next_available_port(start_port=8888, host="127.0.0.1", max_port=65535):
    """
    Finds the first available port on the given host starting from start_port.
    """
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Try to bind to the port
                s.bind((host, port))
                return port
            except OSError:
                # Port is likely in use
                continue
    raise RuntimeError(f"Could not find an open port starting from {start_port}")
