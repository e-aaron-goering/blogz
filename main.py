from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyNewPass@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

blogs = []

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(2500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Title %r>'  % self.title

def get_current_bloglist():
    return Blog.query.all()


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
            return render_template('newpost.html', error_title=error_title, error_body=error_body)

        blog = Blog(title, body)
        db.session.add(blog)
        db.session.commit()
        blog_redirect = "./blog?id=" + str(blog.id)

        return redirect(blog_redirect)
    
    return render_template('newpost.html', title="Add a Blog!")


@app.route("/blog", methods=['POST', 'GET'])
def index():
    if request.args:
        id = request.args.get("id")
        blog = Blog.query.get(id)
        title = blog.title
        body = blog.body
        return render_template('ind-blog.html', title=title, body=body)

    return render_template('blog.html', title="Build-a-Blog!", blogs=get_current_bloglist())


if __name__ == "__main__":
    app.run()