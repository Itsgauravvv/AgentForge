import ctypes
import os
import platform
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

if platform.system() == "Windows":
    lib_name = "agentforge_core.dll"
    sub_folder = "bin"
else:
    lib_name = "libagentforge_core.so"
    sub_folder = "lib"

LIB_DIR = os.path.join(BASE_DIR, "zig-core", "zig-out", sub_folder)
LIB_PATH = os.path.join(LIB_DIR, lib_name)

class ZigRuntime:
    def __init__(self):
        if not os.path.exists(LIB_PATH):
            raise FileNotFoundError(f"Zig library not found at {LIB_PATH}.")
        
        self.lib = ctypes.CDLL(LIB_PATH)
        self.lib.runtime_initialize.restype = ctypes.c_bool
        
        self.lib.runtime_record_event.argtypes = [ctypes.c_char_p]
        self.lib.runtime_record_event.restype = ctypes.c_bool
        
        self.lib.runtime_get_event_count.restype = ctypes.c_int32
        
        # NEW: Map the retrieval function
        self.lib.runtime_get_event.argtypes = [ctypes.c_int32]
        self.lib.runtime_get_event.restype = ctypes.c_char_p
        
        self.lib.runtime_destroy.restype = None

    def initialize(self):
        return self.lib.runtime_initialize()

    def record_event(self, event_type: str, payload: dict):
        event_data = {"type": event_type, "payload": payload}
        json_str = json.dumps(event_data)
        c_string = json_str.encode('utf-8')
        return self.lib.runtime_record_event(c_string)

    def get_event_count(self):
        return self.lib.runtime_get_event_count()

    def get_all_events(self):
        """Extracts the entire event ledger from Zig memory into a Python list."""
        count = self.get_event_count()
        events = []
        for i in range(count):
            # Fetch the raw C string pointer
            c_str = self.lib.runtime_get_event(i)
            if c_str:
                # Decode bytes to string, then parse JSON back into a Python dictionary
                json_str = c_str.decode('utf-8')
                events.append(json.loads(json_str))
        return events

    def destroy(self):
        self.lib.runtime_destroy()