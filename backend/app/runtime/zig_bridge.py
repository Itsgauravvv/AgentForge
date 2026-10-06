import ctypes
import os
import platform

# 1. Figure out the base project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 2. Determine the correct file extension and folder based on your operating system
if platform.system() == "Windows":
    lib_name = "agentforge_core.dll"
    sub_folder = "bin"  # Windows Zig puts DLLs in 'bin'
elif platform.system() == "Darwin":
    lib_name = "libagentforge_core.dylib"
    sub_folder = "lib"  # macOS puts dylibs in 'lib'
else:
    lib_name = "libagentforge_core.so"
    sub_folder = "lib"  # Linux puts .so files in 'lib'

# Construct the final path
LIB_DIR = os.path.join(BASE_DIR, "zig-core", "zig-out", sub_folder)
LIB_PATH = os.path.join(LIB_DIR, lib_name)

class ZigRuntime:
    def __init__(self):
        print(f"Attempting to load Zig library from: {LIB_PATH}")
        if not os.path.exists(LIB_PATH):
            raise FileNotFoundError(f"Zig library not found at {LIB_PATH}. Did you run 'zig build' inside zig-core?")
        
        # Load the library
        self.lib = ctypes.CDLL(LIB_PATH)
        
        # Map the function signatures
        self.lib.runtime_get_version.restype = ctypes.c_int32
        self.lib.runtime_initialize.restype = ctypes.c_bool

    def get_version(self):
        return self.lib.runtime_get_version()

    def initialize(self):
        return self.lib.runtime_initialize()

if __name__ == "__main__":
    runtime = ZigRuntime()
    
    version = runtime.get_version()
    is_init = runtime.initialize()
    
    print("\n--- Python to Zig Connection Successful! ---")
    print(f"Zig Runtime Version: {version}")
    print(f"Zig Initialization:  {is_init}")