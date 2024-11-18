#shreyas its not complete yet. i am working on it . i will not do it now. 
#contributed by madhan
from flask import Flask, request, render_template, redirect, flash, url_for, session,jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_cors import CORS
from datetime import timedelta
import os
import MySQLdb

# Flask app setup
app = Flask(__name__)


# Configuration
app.config['SECRET_KEY'] = os.urandom(24)  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'madhan')  
app.config['MYSQL_DB'] = 'bms'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

mysql = MySQL(app)

# Routes
booked_seats = []

@app.route('/')
def index():
    return render_template('index.html', booked_seats=booked_seats)

@app.route('/book_seat', methods=['POST'])
def book_seat():
    data = request.json
    seat_number = data.get('seat_number')
    
    if seat_number in booked_seats:
        # If trying to unbook a seat
        booked_seats.remove(seat_number)
        return jsonify({'status': 'success', 'action': 'unbooked'})
    else:
        # If booking a new seat
        booked_seats.append(seat_number)
        return jsonify({'status': 'success', 'action': 'booked'})
    
@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))

        flash('Invalid email or password', 'error')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')

        if not all([firstname, lastname, email, password]):
            flash('All fields are required!', 'error')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)

        try:
            with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
                # Check if email already exists
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                if cursor.fetchone():
                    flash('Email already registered!', 'error')
                    return redirect(url_for('signup'))

                cursor.execute(
                    'INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)',
                    (firstname, lastname, email, hashed_password)
                )
                mysql.connection.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {e}', 'error')

    return render_template('signup.html')

# @app.route('/search', methods=['GET'])
# def filter_movies():
#     language = request.args.get('language', '').strip().lower()
#     format_type = request.args.get('format', '').strip().lower()

#     # Filter movies based on language and format
#     filtered_movies = []
#     for movie in movies_list:
#         if (not language or movie['language'].lower() == language) and \
#            (not format_type or format_type in [f.lower() for f in movie['formats']]):
#             filtered_movies.append(movie)

#     return render_template('movies_list.html', movies=filtered_movies)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Movie database
movies_list = [
    {'title': 'Inception', 'language': 'English', 'formats': ['2D', '3D'], 'rating': 86},
    {'title': 'Dangal', 'language': 'Hindi', 'formats': ['2D'], 'rating': 92},
    {'title': 'Kantara', 'language': 'Kannada', 'formats': ['2D'], 'rating': 88},
    {'title': 'Avatar', 'language': 'English', 'formats': ['3D'], 'rating': 89},
    {'title': 'Bahubali', 'language': 'Hindi', 'formats': ['2D', '3D'], 'rating': 85},
    {'title': 'KGF', 'language': 'Kannada', 'formats': ['2D'], 'rating': 90}
]

@app.route('/search', methods=['GET'])
def filter_movies():
    language = request.args.get('language', '').strip()
    format_type = request.args.get('format', '').strip()
    
    # Print debugging information
    print(f"\nReceived request with:")
    print(f"Language: '{language}'")
    print(f"Format: '{format_type}'")
    
    filtered_movies = movies_list
    
    if language:
        filtered_movies = [movie for movie in filtered_movies 
                         if movie['language'] == language]
        print(f"After language filter: {len(filtered_movies)} movies")
    
    if format_type:
        filtered_movies = [movie for movie in filtered_movies 
                         if format_type in movie['formats']]
        print(f"After format filter: {len(filtered_movies)} movies")
    
    print(f"Returning movies: {filtered_movies}")
    return jsonify(filtered_movies)



# @app.route('/movies', methods=['GET'])
# def filter_movies():
#     language = request.args.get('language', '')
#     format_type = request.args.get('format', '')

#     try:
#         with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
#             query = 'SELECT * FROM movies WHERE 1=1'
#             params = []
#             if language:
#                 query += ' AND language = %s'
#                 params.append(language)
#             if format_type:
#                 query += ' AND FIND_IN_SET(%s, formats)'
#                 params.append(format_type)

#             cursor.execute(query, tuple(params))
#             movies = cursor.fetchall()
#     except Exception as e:
#         flash(f'Error fetching movies: {e}', 'error')
#         movies = []

#     return render_template('movies.html', movies=movies)

@app.route('/movies')
def movies():
    return render_template('movies.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        first_name = request.form.get('FirstName')
        last_name = request.form.get('LastName')
        email = request.form.get('Email')
        phone_number = request.form.get('PhoneNumber')
        message = request.form.get('Message')

        if not all([first_name, last_name, email, message]):
            flash('Please fill all required fields!', 'error')
            return redirect(url_for('contact'))

        try:
            with mysql.connection.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO contacts (first_name, last_name, email, phone, message) VALUES (%s, %s, %s, %s, %s)',
                    (first_name, last_name, email, phone_number, message)
                )
                mysql.connection.commit()
                flash('Message sent successfully!', 'success')
                return redirect(url_for('contact'))
        except Exception as e:
            flash(f'Failed to send message: {e}', 'error')

    return render_template('contact.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# print(booked_seats)


if __name__ == '__main__':
    app.run(debug=True)
