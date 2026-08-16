import os
import sqlite3
import base64
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "eduface_secure_admin_session_key_2026"
DB_FILE = "face_db.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT, surname TEXT, 
                        roll_no TEXT, class_section TEXT,
                        UNIQUE(roll_no, class_section))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER, date TEXT, status TEXT,
                        FOREIGN KEY(student_id) REFERENCES students(id))''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            s.class_section, 
            COUNT(DISTINCT s.id) AS total_students,
            COUNT(DISTINCT CASE WHEN a.date = date('now') AND a.status = 'Present' THEN a.id END) AS present_today
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        GROUP BY s.class_section
    ''')
    class_reports = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', class_reports=class_reports)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == "Admin2026":
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = "Invalid administrator password. Access denied."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (first_name, surname, roll_no, class_section) VALUES (?, ?, ?, ?)",
                           (data['first_name'], data['surname'], data['roll_no'], data['class_section']))
            student_id = cursor.lastrowid
            
            for angle, b64_str in data['images'].items():
                if b64_str:
                    img_data = base64.b64decode(b64_str.split(',')[1])
                    with open(f"static/uploads/{student_id}_{angle}.jpg", "wb") as f:
                        f.write(img_data)
            
            conn.commit()
            return jsonify({"status": "success", "message": "Student successfully registered!"})
        except sqlite3.IntegrityError:
            return jsonify({"status": "error", "message": "This roll number is already taken in this specific class."}), 400
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@app.route('/scan', methods=['POST'])
def scan():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, surname FROM students ORDER BY id DESC LIMIT 1")
    student = cursor.fetchone()
    
    if student:
        student_id = student[0]
        full_name = f"{student[1]} {student[2]}"
        
        cursor.execute("SELECT id, status FROM attendance WHERE student_id = ? AND date = date('now')", (student_id,))
        duplicate_check = cursor.fetchone()
        
        if duplicate_check:
            conn.close()
            return jsonify({"status": "success", "name": full_name, "message": f"Attendance already submitted today as {duplicate_check[1]}!"})
        
        cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, date('now'), 'Present')", (student_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "name": full_name, "message": "Attendance marked Present!"})
        
    conn.close()
    return jsonify({"status": "error", "message": "No registered students found."}), 400

@app.route('/admin', methods=['GET', 'POST', 'DELETE'])
def admin():
    if not session.get('admin_logged_in'):
        if request.method in ['POST', 'DELETE']:
            return jsonify({"status": "error", "message": "Unauthorized session status."}), 401
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        student_id = data['student_id']
        date = data['date']
        status = data.get('status', 'Present')
        
        cursor.execute("SELECT id FROM attendance WHERE student_id = ? AND date = ?", (student_id, date))
        existing_log = cursor.fetchone()
        
        if existing_log:
            cursor.execute("UPDATE attendance SET status = ? WHERE id = ?", (status, existing_log[0]))
        else:
            cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (student_id, date, status))
            
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
        
    if request.method == 'DELETE':
        student_id = request.args.get('student_id')
        rec_id = request.args.get('id')
        
        if student_id:
            cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            conn.close()
            return jsonify({"status": "success"})
        elif rec_id:
            cursor.execute("DELETE FROM attendance WHERE id = ?", (rec_id,))
            conn.commit()
            conn.close()
            return jsonify({"status": "success"})

    cursor.execute('''SELECT a.id, s.first_name, s.surname, s.roll_no, s.class_section, a.date, a.status 
                      FROM attendance a JOIN students s ON a.student_id = s.id ORDER BY a.id DESC''')
    records = cursor.fetchall()
    
    cursor.execute("SELECT id, first_name, surname, roll_no, class_section FROM students ORDER BY class_section ASC, roll_no ASC")
    students = cursor.fetchall()
    conn.close()
    return render_template('admin.html', records=records, students=students)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)