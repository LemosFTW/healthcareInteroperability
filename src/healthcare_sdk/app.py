from .transportLayer import RestController

def main():
    app = RestController()
    app.executeServer(port=8000)

if __name__ == "__main__":
    main()