from app import create_app
from app.db import init_db

init_db()           # Initialise database to store valid users
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)