import http.server
import json
import mysql.connector
import cgi
import hashlib
import os

class DatabaseConnection:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASSWORD', 'default_password'),
            port=3306,
            database='HEALTHCARE'
        )
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                password_hashed VARCHAR(255) NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                note_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                content TEXT NOT NULL
            )
        """)

    def close(self):
        self.cursor.close()
        self.conn.close()

class PHRServer(http.server.BaseHTTPRequestHandler):
    def setup_database(self):
        self.db = DatabaseConnection()
        self.db.create_tables()

    def _set_response(self, content_type='application/json'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/notes':
            self.db.cursor.execute("SELECT * FROM notes")
            notes = self.db.cursor.fetchall()
            self._set_response()
            self.wfile.write(json.dumps(notes).encode())

    def handle_notes_post(self, post_data):
        new_note = json.loads(post_data.decode())
        self.db.cursor.execute("INSERT INTO notes (title, content) VALUES (%s, %s)", (new_note['title'], new_note['content']))
        self.db.conn.commit()
        self._set_response()
        self.wfile.write(json.dumps({'message': 'Note added successfully'}).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        if self.path == '/notes':
            self.handle_notes_post(post_data)

    def __init__(self, *args, **kwargs):
        self.db = None
        super().__init__(*args, **kwargs)

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, PHRServer)
    print('Starting server...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        if httpd.db:
            httpd.db.close()
