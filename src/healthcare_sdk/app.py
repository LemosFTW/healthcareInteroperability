from .TransportLayer.restController import RestController

def main():
    app = RestController(port=8000)
    app.executeServer()

if __name__ == "__main__":
    main()