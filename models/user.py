from flask_login import UserMixin
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User(user_data[0], user_data[1], user_data[2])
        return None

    @staticmethod
    def get_by_username(username):
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User(user_data[0], user_data[1], user_data[2])
        return None

    @staticmethod
    def create(username, password):
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                      (username, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return User(user_id, username, password_hash)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password) 