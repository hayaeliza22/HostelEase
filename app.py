from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

def init_db():
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT, type TEXT, description TEXT,
        status TEXT DEFAULT 'Pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT, reason TEXT,
        status TEXT DEFAULT 'Pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sos_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS food_ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT, meal_type TEXT, rating INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/student.html')
def student():
    return send_from_directory('.', 'student.html')

@app.route('/warden.html')
def warden():
    return send_from_directory('.', 'warden.html')

# ALL OTHER ROUTES SAME AS BEFORE...
@app.route('/dashboard_counts')
def dashboard_counts():
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM complaints"); complaints = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM leave_requests"); leave = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM suggestions"); suggestions = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM sos_alerts"); sos = c.fetchone()[0]
    conn.close()
    return jsonify({'complaints': complaints, 'leave': leave, 'suggestions': suggestions, 'sos': sos})

@app.route('/get_complaints')
def get_complaints():
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("SELECT id, student_name, type, description, status FROM complaints ORDER BY created_at DESC")
    data = [{'id': r[0], 'student_name': r[1], 'type': r[2], 'description': r[3], 'status': r[4]} for r in c.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/add_complaint', methods=['POST'])
def add_complaint():
    data = request.json
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("INSERT INTO complaints (student_name, type, description) VALUES (?, ?, ?)",
              (data['student_name'], data['type'], data['description']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Complaint added'})

@app.route('/add_leave', methods=['POST'])
def add_leave():
    data = request.json
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("INSERT INTO leave_requests (student_name, reason) VALUES (?, ?)",
              (data['student_name'], data['reason']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Leave added'})

@app.route('/add_suggestion', methods=['POST'])
def add_suggestion():
    data = request.json
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("INSERT INTO suggestions (message) VALUES (?)", (data['message'],))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Suggestion added'})

@app.route('/get_student_notifications/<student_name>')
def get_student_notifications(student_name):
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()

    c.execute("SELECT type, description, status FROM complaints WHERE student_name=?", (student_name,))
    complaints = [{'type': r[0], 'description': r[1], 'status': r[2]} for r in c.fetchall()]

    c.execute("SELECT reason, status FROM leave_requests WHERE student_name=?", (student_name,))
    leaves = [{'reason': r[0], 'status': r[1]} for r in c.fetchall()]

    conn.close()

    return jsonify({
        'complaints': complaints,
        'leave': leaves
    })

@app.route('/add_sos', methods=['POST'])
def add_sos():
    data = request.json
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("INSERT INTO sos_alerts (student_name) VALUES (?)", (data['student_name'],))
    conn.commit()
    conn.close()
    return jsonify({'message': 'SOS sent'})

@app.route('/add_food_rating', methods=['POST'])  # 🔥 MISSING ROUTE ADDED!
def add_food_rating():
    data = request.json
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("INSERT INTO food_ratings (meal_type, rating) VALUES (?, ?)",
              (data['meal_type'], data['rating']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Food rating added'})

# [Keep all get_ routes same as before]
@app.route('/get_leave')
def get_leave():
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("SELECT id, student_name, reason, status FROM leave_requests ORDER BY created_at DESC")
    data = [{'id': r[0], 'student_name': r[1], 'reason': r[2], 'status': r[3]} for r in c.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/get_suggestions')
def get_suggestions():
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("SELECT message FROM suggestions ORDER BY created_at DESC")
    data = [{'message': r[0]} for r in c.fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/update_complaint_status', methods=['POST'])
def update_complaint_status():
    data = request.json
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("UPDATE complaints SET status=? WHERE id=?",
              (data['status'], data['id']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Complaint status updated'})

@app.route('/update_leave_status', methods=['POST'])
def update_leave_status():
    data = request.json
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("UPDATE leave_requests SET status=? WHERE id=?",
              (data['status'], data['id']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Leave status updated'})

@app.route('/get_sos')
def get_sos():
    conn = sqlite3.connect('hostel.db')
    c = conn.cursor()
    c.execute("SELECT student_name, created_at as time FROM sos_alerts ORDER BY created_at DESC")
    data = [{'student_name': r[0], 'time': r[1]} for r in c.fetchall()]
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    init_db()
    print("🚀 FULLSTACK APP READY! http://127.0.0.1:5000")
    app.run(debug=True, port=5000)

