from flask import Flask, render_template,request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///info.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(150), nullable=False) 
    name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  
            return redirect(url_for('profile')) 
        else:
            return "Invalid credentials. Try again."

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        image = request.files['image']
        name = request.form['name']
        birthday = request.form['birthday']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']

        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('An account with this username already exists. Please choose a different one.', 'error')
            return render_template('register.html')  

        hashed_password = generate_password_hash(password)

        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join('static/uploads', filename)
            image.save(image_path)
            db_image_path = f'uploads/{filename}'
        else:
            db_image_path = ''

        new_user = User(
            image=db_image_path,
            name=name,
            birthday=birthday,
            address=address,
            username=username,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))

    
    birth_date = datetime.strptime(user.birthday, '%Y-%m-%d')
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    return render_template('profile.html', user=user, age=age)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    