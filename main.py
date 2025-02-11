from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
import werkzeug
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['UPLOAD_FOLDER'] = 'static/files'

# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB


class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET","POST"])
def register():

     # get the user input from the form 
 if request.method == "POST":
    
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    hashed_password = werkzeug.security.generate_password_hash(password, method='scrypt', salt_length=8)



    if not name or not email or not password:
        return "Error: All fields are required.", 404
    #create new user 

    new_user = User(email=email, name=name, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    print("The new user was created")

 
    return render_template('secrets.html', name=request.form.get('name'))
 return render_template('register.html')




@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/secrets')
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    pass


@app.route('/download')
def download():
    return send_from_directory(
        'static/files','cheat_sheet.pdf', as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)
