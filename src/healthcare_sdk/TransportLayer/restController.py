from .adapter import Adapter
from fastapi import FastAPI
import uvicorn

app = FastAPI()

class RestController(Adapter):
    """Implements the Adapter interface for RESTful communication"""
    def __init__(self):
        super().__init__()

    @app.get("/health")
    def health_check():
        return {"status": "ok"}
    
    # @app.get("/listMensages")
    # def list_messages():
    #     return {"messages": []}
    
    # @app.post("/processMessage")
    # def process_message(json: dict):
    #     return {"status": "Message received", "message": json}
    
    def executeServer(self, port : int = 8000):
        uvicorn.run(app, port=port)