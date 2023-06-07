# server
import hmac
import sqlite3
import json



class DatabaseManager():
    def __init__(self, password, username, user_type):
        self.password = password
        self.username = username
        self.user_type = user_type
        self.key = '_retdyu_@#1hd99'

    def __encript_password(self):
        

        encripted_password = hmac.new(key=self.key.encode(), msg=self.password.encode(),digestmod="sha256")
        return encripted_password.hexdigest()


    def register(self):
        encripted_password = self.__encript_password()
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        
        try:
            # Check if the username already exists in the 'users' table
            cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', (self.username,))
            result = cursor.fetchone()
            if result[0] > 0:
                # Username already exists, return False to indicate registration failure
                connection.close()
                return False
            else:
                cursor.execute('INSERT INTO users (username, password, type) VALUES (?, ?, ?)', (self.username, encripted_password, self.user_type))
        except sqlite3.OperationalError as e:
            cursor.execute('CREATE TABLE users (username TEXT, password TEXT, type TEXT)')
            cursor.execute('INSERT INTO users (username, password, type) VALUES (?, ?, ?)', (self.username, encripted_password, self.user_type))
        connection.commit()
        connection.close()
        return True


    def login(self):
        encripted_password = self.__encript_password()
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (self.username,))
        user = cursor.fetchone()
        if user is not None and user[1] == encripted_password:
            return True, user[2]
        return False
 
