import subprocess
import uuid
import os
import tempfile

class SandboxManager:
    def __init__(self):
        # Generate a unique name for this execution container
        self.container_name = f"forge-sandbox-{uuid.uuid4().hex[:8]}"
        self.is_running = False

    def start(self):
        """Starts a restricted Docker container in the background."""
        print(f"Starting sandbox container: {self.container_name}")
        
        # We enforce limits: no network access, max 512MB RAM, max 1 CPU core
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

    def execute_python_code(self, code: str) -> dict:
        """Writes code to a file, copies it to the sandbox, and runs it."""
        if not self.is_running:
            raise RuntimeError("Sandbox is not running.")
            
        # 1. Save the code to a temporary file on the host machine
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            host_file_path = temp_file.name

        try:
            # 2. Copy the file into the isolated container's /workspace
            container_file_path = f"/workspace/script.py"
            copy_cmd = ["docker", "cp", host_file_path, f"{self.container_name}:{container_file_path}"]
            subprocess.run(copy_cmd, check=True)

            # 3. Execute the code inside the container with a 10-second timeout
            exec_cmd = ["docker", "exec", self.container_name, "python", container_file_path]
            
            result = subprocess.run(
                exec_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Error: Execution timed out (exceeded 10 seconds)."}
        finally:
            # Clean up the temporary file on the host
            if os.path.exists(host_file_path):
                os.remove(host_file_path)

    def cleanup(self):
        """Forcefully destroys the container."""
        if self.is_running:
            print(f"Destroying sandbox: {self.container_name}")
            subprocess.run(["docker", "rm", "-f", self.container_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.is_running = False