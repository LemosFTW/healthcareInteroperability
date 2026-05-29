from .adapter import Adapter
from fastapi import FastAPI
import uvicorn


class RestController(Adapter):
    """Implements the Adapter interface for RESTful communication"""

    def __init__(self):
        super().__init__()
        self.app = FastAPI()
        self.app.add_api_route("/health", self._health_check, methods=["GET"])

    def _health_check(self):
        return {"status": "ok"}

    def add_endpoint(self, path: str, method: str, handler):
        method_lower = method.lower()
        if method_lower == "get":
            self.app.get(path)(handler)
        elif method_lower == "post":
            self.app.post(path)(handler)
        elif method_lower == "put":
            self.app.put(path)(handler)
        elif method_lower == "delete":
            self.app.delete(path)(handler)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def executeServer(self, port: int = 8000):
        uvicorn.run(self.app, port=port)