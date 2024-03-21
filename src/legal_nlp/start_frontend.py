import subprocess

def main():
    # Launch Streamlit frontend
    frontend_process = subprocess.Popen(["streamlit", "run", "frontend/🏠Home.py"])

    try:
        # Wait for processes to complete
        frontend_process.wait()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        frontend_process.terminate()
    
if __name__ == "__main__":
    main()
