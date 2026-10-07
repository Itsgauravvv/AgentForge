from typing import Dict, Any, Callable

class ToolRegistry:
    """Registry that manages tool definitions and their execution handlers."""
    def __init__(self, sandbox_manager):
        self.sandbox = sandbox_manager
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        # 1. execute_python
        self.register_tool(
            name="execute_python",
            description="Executes a Python code string inside the isolated sandbox and returns stdout/stderr.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "code": {"type": "STRING", "description": "The Python code snippet to execute."}
                },
                "required": ["code"]
            },
            handler=lambda args: self.sandbox.execute_python_code(args.get("code", ""))
        )

        # 2. write_file
        self.register_tool(
            name="write_file",
            description="Writes text content to a file in the sandbox workspace.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "filename": {"type": "STRING", "description": "Name of the file, e.g. analysis.py"},
                    "content": {"type": "STRING", "description": "Text content to save into the file."}
                },
                "required": ["filename", "content"]
            },
            handler=lambda args: self.sandbox.write_file(args.get("filename", ""), args.get("content", ""))
        )

        # 3. read_file
        self.register_tool(
            name="read_file",
            description="Reads the text content of a file from the sandbox workspace.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "filename": {"type": "STRING", "description": "Name of the file to read."}
                },
                "required": ["filename"]
            },
            handler=lambda args: self.sandbox.read_file(args.get("filename", ""))
        )

        # 4. list_files
        self.register_tool(
            name="list_files",
            description="Lists all files in the current sandbox workspace directory.",
            parameters={
                "type": "OBJECT",
                "properties": {}
            },
            handler=lambda args: self.sandbox.list_files()
        )

    def register_tool(self, name: str, description: str, parameters: dict, handler: Callable):
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters
        }
        self._handlers[name] = handler

    def get_declarations(self):
        """Returns tool declarations formatted for LLM tool consumption."""
        return list(self._tools.values())

    def execute_tool(self, name: str, args: dict) -> dict:
        """Executes a requested tool safely."""
        handler = self._handlers.get(name)
        if not handler:
            return {"success": False, "error": f"Tool '{name}' not found."}
        try:
            return handler(args)
        except Exception as e:
            return {"success": False, "error": str(e)}