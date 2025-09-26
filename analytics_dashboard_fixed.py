"""Legacy launcher to keep CLI scripts compatible with the Streamlit dashboard."""
import subprocess
import sys


def main() -> None:
    cmd = [sys.executable, "-m", "streamlit", "run", "apps/dashboard/app.py"]
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
