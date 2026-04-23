import os
import signal
import subprocess
import sys
import time


def main() -> int:
    env = os.environ.copy()
    processes = [
        subprocess.Popen([sys.executable, 'main.py'], env=env),
        subprocess.Popen(['gunicorn', 'web_server:app', '--bind', f"0.0.0.0:{env.get('PORT', '8000')}", '--workers', '1', '--threads', '4', '--timeout', '120'], env=env),
    ]

    def stop_all(*_args):
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
        deadline = time.time() + 10
        while time.time() < deadline:
            alive = [p for p in processes if p.poll() is None]
            if not alive:
                break
            time.sleep(0.2)
        for proc in processes:
            if proc.poll() is None:
                proc.kill()

    signal.signal(signal.SIGTERM, stop_all)
    signal.signal(signal.SIGINT, stop_all)

    while True:
        for proc in processes:
            code = proc.poll()
            if code is not None:
                stop_all()
                return code
        time.sleep(1)


if __name__ == '__main__':
    raise SystemExit(main())
