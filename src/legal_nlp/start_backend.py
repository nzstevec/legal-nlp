import subprocess
from backend.config import Config as BackendConfig

def main():
    # Launch FastAPI backend
    backend_process = subprocess.Popen([
        "uvicorn",
        "launch:app",
        f"--host={BackendConfig.HOST}",
        f"--port={BackendConfig.PORT}",
        "--reload"
    ], cwd="./backend")
    
    try:
        # Wait for processes to complete
        backend_process.wait()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        backend_process.terminate()

if __name__ == "__main__":
    main()
