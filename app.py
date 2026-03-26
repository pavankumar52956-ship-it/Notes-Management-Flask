from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "myverysecretkey" 

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",       
        password="Pavan@2010", # UPDATE THIS TO YOUR PASSWORD
        database="notesdb"
    )

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/viewall')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (username, email, hashed_pw))
            conn.commit()
            flash("Registration successful!", "success")
            return redirect('/login')
        except:
            flash("Username already taken.", "danger")
        finally:
            cur.close()
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/viewall')
        else:
            flash("Invalid credentials.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/addnote', methods=['GET', 'POST'])
def addnote():
    if 'user_id' not in session: return redirect('/login')
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO notes (title, content, user_id) VALUES (%s, %s, %s)",
                    (title, content, session['user_id']))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/viewall')
    return render_template('addnote.html')

@app.route('/viewall')
def viewall():
    if 'user_id' not in session: return redirect('/login')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM notes WHERE user_id = %s", (session['user_id'],))
    notes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('viewnotes.html', notes=notes)

@app.route('/viewnotes/<int:note_id>')
def viewnotes(note_id):
    if 'user_id' not in session: return redirect('/login')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM notes WHERE id = %s AND user_id = %s", (note_id, session['user_id']))
    note = cur.fetchone()
    cur.close()
    conn.close()
    if not note: return redirect('/viewall')
    return render_template('singlenote.html', note=note)

@app.route('/updatenote/<int:note_id>', methods=['GET', 'POST'])
def updatenote(note_id):
    if 'user_id' not in session: return redirect('/login')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        cur.execute("UPDATE notes SET title=%s, content=%s WHERE id=%s AND user_id=%s",
                    (request.form['title'], request.form['content'], note_id, session['user_id']))
        conn.commit()
        return redirect('/viewall')
    cur.execute("SELECT * FROM notes WHERE id=%s AND user_id=%s", (note_id, session['user_id']))
    note = cur.fetchone()
    return render_template('updatenote.html', note=note)

@app.route('/deletenote/<int:note_id>', methods=['POST'])
def deletenote(note_id):
    if 'user_id' not in session: return redirect('/login')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id=%s AND user_id=%s", (note_id, session['user_id']))
    conn.commit()
    return redirect('/viewall')

if __name__ == '__main__':
    app.run(debug=True)