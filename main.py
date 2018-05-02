from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'skfiti83hgqkjd'

password_confirmation = ''
login_check = False
user_err = ''
password_err = ''
password_confrimation_err = ''

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<Username %r>' % self.username

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Title %r>'  % self.title

def get_current_bloglist():
    return Blog.query.all()

def get_current_userlist():
    return User.query.all()

def is_loggedin():
    if 'username' in session:
        return True
    else:
        return False

def username_error(username):
    user = User.query.filter_by(username=username).first()

    if not username:
        return "that's not a valid username"
    if ' ' in username:
        return "that's not a valid username"
    if 4 > len(username):
        return "that's not a valid username"
    if  len(username) > 20:
        return "that's not a valid username"
    if user:
        return "that username already exists"
    return ''

def password_error(password):
    if not password:
        return "that's not a valid password"
    if ' ' in password:
        return "that's not a valid password"
    if 4 > len(password):
        return "that's not a valid password"
    if len(password) > 20:
        return "that's not a valid password"
    return ''

def password_confirmation_error(password, password_confirmation):
    if not password_confirmation:
        return "passwords don't match"
    if password != password_confirmation:
        return "passwords don't match"
    return ''

@app.before_request
def require_login():
    global login_check
    login_check = is_loggedin()
    allowed_routes = ['index', 'login', 'signup', 'blog', 'index', 'ind_blog', 'single_user']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/signup",methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirmation = request.form['password-confirmation']
    
        user_err = username_error(username)
        password_err = password_error(password)
        password_confirmation_err = password_confirmation_error(password, password_confirmation)

        if user_err or password_err or password_confirmation_err:
            return render_template("signup.html", title='Sign Up for Blogz!', login_check=login_check, user_err=user_err, password_err=password_err, 
                                    password_confirmation_err=password_confirmation_err) 
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    
    return render_template("signup.html", title='Sign Up for Blogz!', login_check=login_check)

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            newpost_redirect = "/newpost?user=" + str(user.username)
            return redirect(newpost_redirect)
        else:
            if not user:
                error = "Username does not exist or is incorrect!"
                return render_template("login.html", title='Blogz!', login_check=login_check, error=error)
            elif user.password != password:
                error = "Password is incorrect, try again!"
                return render_template("login.html", title='Blogz!', login_check=login_check, error=error)            

    return render_template("login.html", title='Blogz!', login_check=login_check)

@app.route("/logout")
def logout():
    del session['username']
    return redirect('/blog')

@app.route("/singleUser")
def single_user():
    return '<h1>Welcome, User</h1>'


@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error_title = ''
        error_body = ''

        if not title:
            error_title = "Please fill in the title"
        if not body:
            error_body = "Please fill in the body"
        if not title or not body:
            return render_template('newpost.html', title='Add a Blog', login_check=login_check, error_title=error_title, error_body=error_body)

        owner = User.query.filter_by(username=session['username']).first()
        blog = Blog(title, body, owner)
        db.session.add(blog)
        db.session.commit()

        return render_template('ind-blog.html', title="Add a Blog!", login_check=login_check, blog=blog)
    
    return render_template('newpost.html', title="Add a Blog!", login_check=login_check)


@app.route("/blog", methods=['POST', 'GET'])
def blog():
    if request.args:
        username = request.args.get('user')
        owner = User.query.filter_by(username=username).first()
        title = owner.username + "'s Blogz"
        bloglist = Blog.query.filter_by(owner=owner).all()
        return render_template('singleUser.html', title=title, login_check=login_check, bloglist=bloglist)

    bloglist = get_current_bloglist()
    return render_template('blog.html', title='Blogz!', login_check=login_check, bloglist=bloglist)

@app.route("/ind-blog", methods=['POST', 'GET'])
def ind_blog():
    str_id = request.args.get('id')
    int_id = int(str_id)
    the_blog = Blog.query.filter_by(id=int_id).first()
    return render_template('ind-blog.html', title=the_blog.title, login_check=login_check, blog=the_blog)

    
@app.route('/')
def index():
    userlist = get_current_userlist()
    return render_template('index.html', title='Blogz!', login_check=login_check, 
        userlist=userlist)


if __name__ == "__main__":
    app.run()