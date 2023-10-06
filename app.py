from dotenv import load_dotenv

from app import get_app

if __name__ == "__main__":
    load_dotenv()

    app = get_app()
    app.run()
