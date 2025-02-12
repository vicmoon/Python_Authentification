from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, session
import werkzeug
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")



# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"


# CREATE TABLE IN DB , add UserMixin


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

# create a user loader callback 
@login_manager.user_loader
def load_user(id):
    with db.session() as session:
     return session.get(User, int(id))


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
    #check if user exists 

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("User already exists. Please log in.", "warning")
        print("THe user exists already. Log in.")
        return redirect(url_for('login'))


    #create new user 

    new_user = User(email=email, name=name, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)

    # Store name in session
    session['name'] = name

    print("The new user was created")

 
    return render_template('secrets.html', name=name)
 return render_template('register.html')




@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        #check if the user exists by email address 

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("secrets"))
        
        flash("Invalid email or password", "warning")


    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    logout_user()

    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory(
        'static/files','cheat_sheet.pdf', as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)
