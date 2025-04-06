
import sys
import os
import re
from io import StringIO

if __name__ == "__main__":
    from tools import Tools
else:
    from sources.tools.tools import Tools

class PyInterpreter(Tools):
    """
    This class is a tool to allow agent for python code execution.
    """
    def __init__(self):
        super().__init__()
        self.tag = "python"

    def execute(self, codes:str, safety = False) -> str:
        """
        Execute python code.
        """
        output = ""
        if safety and input("Execute code ? y/n") != "y":
            return "Code rejected by user."
        stdout_buffer = StringIO()
        sys.stdout = stdout_buffer
        global_vars = {
            '__builtins__': __builtins__,
            'os': os,
            'sys': sys,
        }
        code = '\n\n'.join(codes)
        try:
            try:
                buffer = exec(code, global_vars)
                print(buffer)
                if buffer is not None:
                    output = buffer + '\n'
            except Exception as e:
                return "code execution failed:" + str(e)
            output = stdout_buffer.getvalue()
        finally:
            sys.stdout = sys.__stdout__
        return output

    def interpreter_feedback(self, output:str) -> str:
        """
        Provide feedback based on the output of the code execution
        """
        if self.execution_failure_check(output):
            feedback = f"[failure] Error in execution:\n{output}"
        else:
            feedback = "[success] Execution success, code output:\n" + output
        return feedback

    def execution_failure_check(self, feedback:str) -> bool:
        """
        Check if the code execution failed.
        """
        error_patterns = [
            r"expected", 
            r"errno", 
            r"failed", 
            r"traceback", 
            r"invalid", 
            r"unrecognized", 
            r"exception", 
            r"syntax", 
            r"crash", 
            r"segmentation fault", 
            r"core dumped"
        ]
        combined_pattern = "|".join(error_patterns)
        if re.search(combined_pattern, feedback, re.IGNORECASE):
            return True
        return False

if __name__ == "__main__":
    text = """
For Python, let's also do a quick check:

```python
print("Hello from Python!")
```

If these work, you'll see the outputs in the next message. Let me know if you'd like me to test anything specific! 

here is a save test
```python:tmp.py

def print_hello():
    hello = "Hello World"
    print(hello)
```
"""
    py = PyInterpreter()
    codes, save_path = py.load_exec_block(text)
    py.save_block(codes, save_path)
    print(py.execute(codes))