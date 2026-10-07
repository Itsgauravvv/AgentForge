const std = @import("std");

const allocator = std.heap.c_allocator;

var event_log: [][]u8 = &[_][]u8{};
var event_count: usize = 0;
var event_capacity: usize = 0;
var is_initialized: bool = false;

export fn runtime_initialize() bool {
    if (!is_initialized) {
        event_log = &[_][]u8{};
        event_count = 0;
        event_capacity = 0;
        is_initialized = true;
    }
    return true;
}

export fn runtime_record_event(event_json: [*c]const u8) bool {
    if (!is_initialized) return false;
    
    const event_str = std.mem.span(event_json);
    
    // Manually allocate space for the string plus 1 extra byte for the null terminator
    const stored_str = allocator.alloc(u8, event_str.len + 1) catch return false;
    
    // Copy the actual string data into our newly allocated memory
    @memcpy(stored_str[0..event_str.len], event_str);
    
    // Explicitly set the final byte to 0 so Python knows where the string ends
    stored_str[event_str.len] = 0;
    
    if (event_count >= event_capacity) {
        const new_cap = if (event_capacity == 0) 8 else event_capacity * 2;
        const new_log = allocator.realloc(event_log, new_cap) catch return false;
        event_log = new_log;
        event_capacity = new_cap;
    }
    
    event_log[event_count] = stored_str;
    event_count += 1;
    
    return true;
}

export fn runtime_get_event_count() i32 {
    if (!is_initialized) return 0;
    return @as(i32, @intCast(event_count));
}

export fn runtime_get_event(index: i32) [*c]const u8 {
    if (!is_initialized or index < 0 or index >= event_count) {
        return null; 
    }
    const idx = @as(usize, @intCast(index));
    return event_log[idx].ptr;
}

export fn runtime_destroy() void {
    if (is_initialized) {
        var i: usize = 0;
        while (i < event_count) : (i += 1) {
            allocator.free(event_log[i]);
        }
        if (event_capacity > 0) {
            allocator.free(event_log);
        }
        is_initialized = false;
        event_count = 0;
        event_capacity = 0;
    }
}