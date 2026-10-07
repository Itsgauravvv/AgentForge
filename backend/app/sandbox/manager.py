import subprocess
import uuid
import os
import tempfile

class SandboxManager:
    def __init__(self):
        self.container_name = f"forge-sandbox-{uuid.uuid4().hex[:8]}"
        self.is_running = False

    def start(self):
        """Starts a restricted Docker container in the background."""
        cmd = [
            "docker", "run", "-d",
            "--name", self.container_name,
            "--network", "none",
            "--memory", "512m",
            "--cpus", "1.0",
            "agentforge-sandbox"
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.is_running = True

    def write_file(self, filename: str, content: str) -> dict:
        """Writes arbitrary file content directly into the container's /workspace."""
        if not self.is_running:
            raise RuntimeError("Sandbox is not running.")
        
        # Prevent path traversal attacks like '../../etc/passwd'
        safe_filename = os.path.basename(filename)
        container_path = f"/workspace/{safe_filename}"

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            copy_cmd = ["docker", "cp", tmp_path, f"{self.container_name}:{container_path}"]
            subprocess.run(copy_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return {"success": True, "message": f"Wrote {len(content)} bytes to {safe_filename}"}
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def read_file(self, filename: str) -> dict:
        """Reads a file from the container's /workspace."""
        if not self.is_running:
            raise RuntimeError("Sandbox is not running.")
        
        safe_filename = os.path.basename(filename)
        exec_cmd = ["docker", "exec", self.container_name, "cat", f"/workspace/{safe_filename}"]
        res = subprocess.run(exec_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return {"success": False, "error": res.stderr.strip() or "File not found"}
        return {"success": True, "content": res.stdout}

    def list_files(self) -> dict:
        """Lists all files present in the container's /workspace."""
        if not self.is_running:
            raise RuntimeError("Sandbox is not running.")
        
        exec_cmd = ["docker", "exec", self.container_name, "ls", "-la", "/workspace"]
        res = subprocess.run(exec_cmd, capture_output=True, text=True)
        return {"success": True, "files": res.stdout.strip()}

    def execute_python_code(self, code: str) -> dict:
        """Executes Python code inside the container with a 10s timeout."""
        if not self.is_running:
            raise RuntimeError("Sandbox is not running.")
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            host_file_path = temp_file.name

        try:
            container_file_path = "/workspace/script.py"
            copy_cmd = ["docker", "cp", host_file_path, f"{self.container_name}:{container_file_path}"]
            subprocess.run(copy_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            exec_cmd = ["docker", "exec", self.container_name, "python", container_file_path]
            result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=10)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Execution timed out (10s limit)."}
        finally:
            if os.path.exists(host_file_path):
                os.remove(host_file_path)

    def cleanup(self):
        """Forcefully destroys the container."""
        if self.is_running:
            subprocess.run(["docker", "rm", "-f", self.container_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.is_running = False