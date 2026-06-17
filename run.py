"""One-command launcher for VisionFlow (backend API + Streamlit UI).

Usage:
    python run.py              # start API (:8000) and UI (:8501) together
    python run.py --reload     # start API with autoreload (dev)
    python run.py --no-ui      # start only the API
    python run.py --api-port 8000 --ui-port 8501

Press Ctrl+C once to stop everything cleanly.
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def _python_executable() -> str:
    """Prefer the project venv interpreter, fall back to the current one."""
    if os.name == "nt":
        venv_py = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        venv_py = PROJECT_ROOT / ".venv" / "bin" / "python"
    return str(venv_py) if venv_py.exists() else sys.executable


def _wait_for_api(url: str, timeout: float = 40.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.8)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Start VisionFlow backend + frontend.")
    parser.add_argument("--api-host", default="127.0.0.1")
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--ui-port", type=int, default=8501)
    parser.add_argument("--reload", action="store_true", help="enable API autoreload")
    parser.add_argument("--no-ui", action="store_true", help="start API only")
    args = parser.parse_args()

    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    py = _python_executable()
    env = dict(os.environ)
    env.setdefault("PYTHONUNBUFFERED", "1")
    api_base = f"http://{args.api_host}:{args.api_port}"
    env.setdefault("API_BASE_URL", api_base)

    procs: list[subprocess.Popen] = []

    print(f"[VisionFlow] Python: {py}")
    print(f"[VisionFlow] Starting API at {api_base} ...")
    api_cmd = [
        py, "-m", "uvicorn", "app.main:app",
        "--host", args.api_host, "--port", str(args.api_port),
    ]
    if args.reload:
        api_cmd.append("--reload")
    procs.append(subprocess.Popen(api_cmd, cwd=str(PROJECT_ROOT), env=env))

    if _wait_for_api(f"{api_base}/health"):
        print("[VisionFlow] API is healthy.")
    else:
        print("[VisionFlow] WARNING: API did not become healthy in time; continuing anyway.")

    if not args.no_ui:
        print(f"[VisionFlow] Starting UI at http://localhost:{args.ui_port} ...")
        ui_cmd = [
            py, "-m", "streamlit", "run", "app/ui/streamlit_app.py",
            "--server.port", str(args.ui_port),
        ]
        procs.append(subprocess.Popen(ui_cmd, cwd=str(PROJECT_ROOT), env=env))

    print("[VisionFlow] All services started. Press Ctrl+C to stop.")

    def _shutdown(*_args) -> None:
        print("\n[VisionFlow] Shutting down ...")
        for p in procs:
            if p.poll() is None:
                try:
                    p.terminate()
                except Exception:
                    pass
        for p in procs:
            try:
                p.wait(timeout=8)
            except Exception:
                p.kill()

    try:
        signal.signal(signal.SIGINT, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    except Exception:
        pass

    try:
        while True:
            for p in procs:
                code = p.poll()
                if code is not None:
                    print(f"[VisionFlow] A process exited (code={code}); stopping the rest.")
                    _shutdown()
                    return code or 0
            time.sleep(1)
    except KeyboardInterrupt:
        _shutdown()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
