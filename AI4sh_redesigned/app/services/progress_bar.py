# Shared loading overlay state. This API provides text and active state, not percentage progress.
from .workspace_context import services

class ProgressBar:
    @staticmethod
    # Set loading active with a string message under the runtime lock.
    # Start/end are not reference-counted; avoid overlapping ownership.
    def start(text="Working…"):
        s = services()
        with s.lock:
            s.progress_state = dict(active=True, text=str(text))

    @staticmethod
    # Clear loading state. This does not cancel the running job or complete its lifecycle.
    def end():
        s = services()
        with s.lock:
            s.progress_state["active"] = False
