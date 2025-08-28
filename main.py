import os, sys, time, signal, subprocess, webbrowser
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Paths definition
ROOT = Path(__file__).resolve().parent
API_APP = "api.api:app"
STREAMLIT_ENTRY = ROOT / "app" / "app.py"


# Helpers definition
def spawn(cmd, *, env=None, cwd=None):
    """
    Start process in a new group (Windows) or in a new session (Unix).
    This allow the system to kill the process in a clean way.
    """
    kwargs = dict(env=env, cwd=cwd)
    if os.name == "nt":
        # New process group in Windows
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    else:
        # New session in Unix
        kwargs["preexec_fn"] = os.setsid
    return subprocess.Popen(cmd, **kwargs)


def kill_tree(p: subprocess.Popen):
    """
    Kill processes
    """
    if not p or p.poll() is not None:
        return
    try:
        if os.name == "nt":
            # Kill processes in Windows
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Kill processes in Unix
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)

    except Exception:
        try:
            p.terminate()
        except Exception:
            pass


def wait_http_ready(url: str, timeout_s: float = 20.0, interval_s: float = 0.5):
    """Wait until URL returns 200 OK (simple health check)."""
    deadline = time.time() + timeout_s
    req = Request(url, headers={"User-Agent": "healthcheck"})
    while time.time() < deadline:
        try:
            with urlopen(req, timeout=3) as r:
                if 200 <= r.status < 300:
                    return True
        except (URLError, HTTPError):
            pass
        time.sleep(interval_s)
    return False


# Main
def run():
    env = os.environ.copy()

    # Define ports
    env.setdefault("PORT_BACKEND", "8000")
    env.setdefault("PORT_FRONTEND", "8501")

    # Define URLs
    backend_url = f"http://127.0.0.1:{env['PORT_BACKEND']}"
    frontend_url_127 = f"http://127.0.0.1:{env['PORT_FRONTEND']}"
    frontend_url_local = f"http://localhost:{env['PORT_FRONTEND']}"

    # Propagate frontend y backend
    env["BACKEND_URL"] = backend_url
    env["ALLOWED_ORIGINS"] = f"{frontend_url_127},{frontend_url_local}"

    # 1) Backend (FastAPI + Uvicorn)
    uvicorn_cmd = [
        sys.executable, "-m", "uvicorn", API_APP,
        "--host", "127.0.0.1", "--port", env["PORT_BACKEND"],
    ]

    # 2) Frontend (Streamlit)
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", str(STREAMLIT_ENTRY),
        "--server.port", env["PORT_FRONTEND"],
        "--server.headless", "true",
        "--server.address", "127.0.0.1",
    ]

    # Start backend
    backend = spawn(uvicorn_cmd, env=env, cwd=str(ROOT))

    # Wait for readiness
    if not wait_http_ready(f"{backend_url}/health", timeout_s=25):
        print("Backend didn't respond to healthcheck.")
        kill_tree(backend)
        sys.exit(1)

    # Start frontend
    frontend = spawn(streamlit_cmd, env=env, cwd=str(ROOT))

    # Wait for readiness
    if not wait_http_ready(f"{frontend_url_127}", timeout_s=25):
        print("Frontend didn't respond.")
        kill_tree(frontend)
        sys.exit(1)

    # Open URL in browser
    try:
        webbrowser.open(frontend_url_127)
    except Exception:
        pass

    # Kill frontend and backend processes
    def shutdown(*_):
        kill_tree(frontend)
        kill_tree(backend)
        sys.exit(0)

    # Shutdown signals
    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    # Exit process when Streamlit or backend is closed
    try:
        exit_codes = [p.wait() for p in (frontend, backend)]
        sys.exit(max(exit_codes))
    finally:
        shutdown()


if __name__ == "__main__":
    run()
