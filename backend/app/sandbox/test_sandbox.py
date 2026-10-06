from manager import SandboxManager

if __name__ == "__main__":
    sandbox = SandboxManager()
    
    try:
        sandbox.start()
        
        # Test 1: A normal, safe piece of code
        print("\n--- Test 1: Simple Math ---")
        safe_code = """
x = 10
y = 20
print(f"The result is {x + y}")
"""
        result = sandbox.execute_python_code(safe_code)
        print("Success:", result["success"])
        print("Output:", result["stdout"])

        # Test 2: Checking security (Who is running the code? What OS?)
        print("\n--- Test 2: Security Check ---")
        security_code = """
import os
import sys
print("Operating System:", sys.platform)
print("Current User:", os.popen('whoami').read().strip())
"""
        result = sandbox.execute_python_code(security_code)
        print("Output:\n" + result["stdout"])
        
    finally:
        # Always clean up, even if the code crashes
        sandbox.cleanup()