import inspect
import os

def _caller_info(stack_depth=3):
    frame = inspect.stack()[stack_depth]
    filename = os.path.basename(frame.filename)
    func = frame.function
    lineno = frame.lineno
    return f"{filename}:{lineno} ({func})"
