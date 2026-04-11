import os
# from dotenv import load_dotenv
# load_dotenv("config.env")

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
GIF_SECRET = os.environ.get("GIF_SECRET")   # Protect endpoint to prevent unauthorised users