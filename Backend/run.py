from flask import Flask
from app import create_app
from dotenv import load_dotenv

app = create_app()

load_dotenv()

if __name__ == "__main__":
    app.run()