from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_mysqldb import MySQL
import io

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password123'
app.config['MYSQL_DB'] = 'file_storage'
app.secret_key = '0207'
mysql = MySQL(app)
@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    print(f"Request method: {request.method}")  
    if request.method == 'POST':
        print(f"Form data: {request.form}")  
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Username: {username}, Password: {password}")

        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cur.execute(query, (username, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=[ 'POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get['username']
        password = request.form.get['password']
        confirm_password = request.form.get['confirm_password']

        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')

        cur = mysql.connection.cursor()
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cur.execute(query, (username, password))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        cur = mysql.connection.cursor()
        query = "SELECT id, filename, uploaded_at FROM files"
        cur.execute(query)
        files = cur.fetchall()
        cur.close()

        return render_template('dashboard.html', username=session['username'], files=files)
    else:
        return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' in session:
        if request.method == 'POST':
            file = request.files['file']
            if file:
                filename = file.filename
                filedata = file.read()
                
                cur = mysql.connection.cursor()
                query = "INSERT INTO files (filename, filedata, uploaded_at) VALUES (%s, %s, NOW())"
                cur.execute(query, (filename, filedata))
                mysql.connection.commit()
                cur.close()

                return redirect(url_for('dashboard'))
        return render_template('upload.html')
    else:
        return redirect(url_for('login'))

@app.route('/download/<int:file_id>')
def download(file_id):
    if 'username' in session:
        cur = mysql.connection.cursor()
        query = "SELECT filename, filedata FROM files WHERE id = %s"
        cur.execute(query, (file_id,))
        file = cur.fetchone()
        cur.close()

        if file:
            filename, filedata = file
            return send_file(
                io.BytesIO(filedata),
                download_name=filename,
                as_attachment=True
            )
    else:
        return redirect(url_for('login'))
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/test_db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT username FROM users LIMIT 1")
        cur.close()
        return "Database connection is successful!"
    except Exception as e:
        return f"Database connection failed: {e}"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
