const std = @import("std");

// The 'export' keyword exposes this function to the C ABI (Application Binary Interface).
// This is what allows Python's ctypes library to see and call it.
export fn runtime_get_version() i32 {
    // We return a simple integer to verify the connection works.
    return 100; // Represents version 1.0.0
}

export fn runtime_initialize() bool {
    // Later, this will allocate memory for our execution state.
    // For now, it just returns true.
    return true;
}