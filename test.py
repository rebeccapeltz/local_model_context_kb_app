# find open port for Windows
import socket

def find_free_port(fallback_port=5500):
    try:
        # Test if the port is available
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", fallback_port))
            return fallback_port
    except OSError:
        # If occupied, let the OS dynamically assign any free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", 0))
            return s.getsockname()[1]

# In your runtime block:
PORT = find_free_port(5500)
