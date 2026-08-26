import os
import sys
import subprocess
import uvicorn

def run_cmd(cmd, cwd=None):
    """Run shell command with cross-platform compatibility."""
    print(f"Running: {' '.join(cmd)} in {cwd or '.'}")
    res = subprocess.run(cmd, cwd=cwd, shell=True)
    if res.returncode != 0:
        print(f"ERROR: Command failed with code {res.returncode}")
        sys.exit(res.returncode)

def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)

    print("=" * 60)
    print("DENGUE OUTBREAK PREDICTION SYSTEM RUNNER")
    print("=" * 60)

    # 1. Install Backend Dependencies
    print("\n[1/4] Installing Python dependencies...")
    run_cmd([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # 2. Install Frontend Dependencies
    print("\n[2/4] Installing React NPM dependencies...")
    run_cmd(["npm", "install"], cwd="frontend")

    # 3. Build Frontend Application
    print("\n[3/4] Building React dashboard bundles...")
    run_cmd(["npm", "run", "build"], cwd="frontend")

    # 4. Launch Unified Application Server
    print("\n[4/4] Starting FastAPI unified server on http://localhost:8000...")
    print("Open http://localhost:8000 in your browser to view the Dengue Dashboard.")
    print("Use Ctrl+C to terminate.")
    print("-" * 60)
    
    # We run uvicorn inside the python process
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
