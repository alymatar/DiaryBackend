from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="diary_db",  # Replace with your database name
        user="postgres",  # Replace with your PostgreSQL username
        password="ali9141353",
        port="5432"
    )
    return conn

# Initialize the database (create table if not exists)
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS diary_entries (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Route to get all diary entries
@app.route('/api/diary-entries', methods=['GET'])
def get_diary_entries():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM diary_entries ORDER BY created_at DESC')
    entries = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(entries)

# Route to create a new diary entry
@app.route('/api/diary-entries', methods=['POST'])
def create_diary_entry():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    if not title or not content:
        return jsonify({"error": "Title and Content are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO diary_entries (title, content) VALUES (%s, %s) RETURNING *',
        (title, content)
    )
    new_entry = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(new_entry), 201

# Route to get a single diary entry by ID
@app.route('/api/diary-entries/<int:entry_id>', methods=['GET'])
def get_diary_entry(entry_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM diary_entries WHERE id = %s', (entry_id,))
    entry = cur.fetchone()
    cur.close()
    conn.close()

    if entry is None:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify(entry)

# Route to update a diary entry
@app.route('/api/diary-entries/<int:entry_id>', methods=['PUT'])
def update_diary_entry(entry_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"error": "Title and Content are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'UPDATE diary_entries SET title = %s, content = %s WHERE id = %s RETURNING *',
        (title, content, entry_id)
    )
    updated_entry = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if updated_entry is None:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify(updated_entry)

# Route to delete a diary entry
@app.route('/api/diary-entries/<int:entry_id>', methods=['DELETE'])
def delete_diary_entry(entry_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM diary_entries WHERE id = %s RETURNING *', (entry_id,))
    deleted_entry = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if deleted_entry is None:
        return jsonify({"error": "Entry not found"}), 404

    return jsonify({"message": "Entry deleted"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
