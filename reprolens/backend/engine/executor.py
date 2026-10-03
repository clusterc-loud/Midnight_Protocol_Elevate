"""Docker execution engine for ReproLens."""
import subprocess
import time
from pathlib import Path
from typing import Tuple


def run_docker(command: str, paper: dict, timeout: int = 300) -> Tuple[str, int, float, int]:
    """
    Run a Docker container with the experiment command.
    Returns: (stdout, return_code, wall_time_seconds, peak_memory_mb)
    """
    repo_path = Path(paper.get("repo_path", paper["path"])).resolve()
    image_name = paper["image_name"]
    
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{repo_path}:/repo",
        "-w", "/repo",
        "--cpus=2", "--memory=4g", "--memory-swap=4g",
        "--network=none", "--pids-limit=256",
        image_name, "bash", "-c", command
    ]
    
    start = time.time()
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1
        )
        
        stdout_lines = []
        for line in proc.stdout:
            print(f"[docker] {line.rstrip()}")
            stdout_lines.append(line)
        
        proc.wait(timeout=timeout)
        wall = time.time() - start
        return "".join(stdout_lines), proc.returncode, wall, 0
        
    except subprocess.TimeoutExpired:
        return "", -1, timeout, 0
    except Exception as e:
        print(f"[ERROR] Docker run failed: {e}")
        return "", -1, 0, 0


def build_docker_image(paper: dict) -> bool:
    """Build Docker image for a paper."""
    dockerfile_path = Path(paper["path"]) / paper["dockerfile"]
    if not dockerfile_path.exists():
        print(f"[ERROR] Dockerfile not found: {dockerfile_path}")
        return False
    
    cmd = ["docker", "build", "-t", paper["image_name"], "-f", str(dockerfile_path), str(Path(paper["path"]).parent)]
    print(f"[BUILD] Building image: {paper['image_name']}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print(f"[ERROR] Docker build failed:\n{result.stderr}")
        return False
    print(f"[BUILD] Image built successfully")
    return True