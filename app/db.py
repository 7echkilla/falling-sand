import sqlite3

DATABASE = "users.db"

def init_db():
    """
    Initialise database to store authorised users
    """

    connection = sqlite3.connect(DATABASE)  # Create files if it doesn't exist
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                access_token TEXT NOT NULL
            )
        """)                                # Table (users): username (unique entries), access_token (must exist) 
    connection.commit()                     # Save changes
    connection.close()                      # Close connection to avoid corruption

def save_user(username, token):
    """
    Store or update user details in database on login
    """

    connection = sqlite3.connect(DATABASE)  # Open database
    connection.execute("""
        INSERT OR REPLACE INTO users (username, access_token) VALUES (?, ?)
    """, (username, token))                 # '?' Placeholders to prevent SQL injection
    connection.commit()                     # Insert new if user doesn't exist, replace if user already exists
    connection.close()

def get_access_token(username):
    """
    Return token if user exists in database; else None
    """

    connection = sqlite3.connect(DATABASE)
    cursor = connection.execute("""
        SELECT access_token FROM users WHERE username = ?
    """, (username,))                       # Point to result (token) for given username
    row = cursor.fetchone()                 # Get one result since username is unique
    connection.close()

    return row[0] if row else None