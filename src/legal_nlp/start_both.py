import subprocess
from time import sleep
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

    sleep(20)
    
    # Launch Streamlit frontend
    frontend_process = subprocess.Popen(["streamlit", "run", "frontend/🏠Home.py"])

    try:
        # Wait for both processes to complete
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    main()
