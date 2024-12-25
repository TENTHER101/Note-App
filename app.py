from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id TEXT PRIMARY KEY,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
                            id TEXT PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            title TEXT NOT NULL,
                            content TEXT NOT NULL,
                            timestamp TEXT NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users (id))''')
        conn.commit()

init_db()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    hashed_password = generate_password_hash(password)
    user_id = str(uuid.uuid4())
    try:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (id, username, password) VALUES (?, ?, ?)', (user_id, username, hashed_password))
            conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'User already exists'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[1], password):
            return jsonify({'user_id': user[0]}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/notes', methods=['GET'])
def get_notes():
    user_id = request.args.get('user_id')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, content, timestamp FROM notes WHERE user_id = ?', (user_id,))
        notes = cursor.fetchall()
    return jsonify([{'id': note[0], 'title': note[1], 'content': note[2], 'timestamp': note[3]} for note in notes])

@app.route('/notes', methods=['POST'])
def add_note():
    data = request.json
    note_id = str(uuid.uuid4())
    user_id = data.get('user_id')
    title = data.get('title')
    content = data.get('content')
    timestamp = datetime.now().isoformat()
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO notes (id, user_id, title, content, timestamp) VALUES (?, ?, ?, ?, ?)', (note_id, user_id, title, content, timestamp))
        conn.commit()
    return jsonify({'message': 'Note added successfully'}), 201

@app.route('/notes/<note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.json
    user_id = data.get('user_id')
    title = data.get('title')
    content = data.get('content')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE notes SET title = ?, content = ? WHERE id = ? AND user_id = ?', (title, content, note_id, user_id))
        conn.commit()
    return jsonify({'message': 'Note updated successfully'})

@app.route('/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    user_id = request.args.get('user_id')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', (note_id, user_id))
        conn.commit()
    return jsonify({'message': 'Note deleted successfully'})

@app.route('/notes/<note_id>', methods=['GET'])
def get_note(note_id):
    user_id = request.args.get('user_id')
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, content, timestamp FROM notes WHERE id = ? AND user_id = ?', (note_id, user_id))
        note = cursor.fetchone()
    if note:
        return jsonify({'id': note[0], 'title': note[1], 'content': note[2], 'timestamp': note[3]})
    return jsonify({'message': 'Note not found'}), 404

if __name__ == '__main__':
    app.run(debug=False)
