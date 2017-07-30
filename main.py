from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Alpha123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'ttdgdsdJAJDdbhsuafddbsf29592'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(400))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs =  db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

# additional route handlers for addeded app features
@app.before_request
def require_login():
    allowed_routes = ['index', 'login', 'signup', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():

    blogers = User.query.all()

    return render_template('index.html', title='Blogz', users=blogers)

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash("Login Succesful", "success")
            return redirect('/newpost')
        elif user and not user.password == password:
            flash("Incorrect Password", "error")
        elif username == "" or password == "":
            flash("Invalid Entry", "error")
        else:
            flash("User Does Not Exist", "error")

    if request.method == "GET":
        signup = request.args.get('signup')
        if signup:
            return redirect('/signup')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        signup = False
        username = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if username == "" or password == "" or verify == "":
            flash("One Or More Invalid Entries", "error")
            return render_template('signup.html')
        elif len(list(password)) < 8:
            flash("Password Must Be At Least 8 Characters Long", "error")
            return render_template('signup.html', email=username)
        elif not password == verify:
            flash("Password Does Not Match", "error")
            return render_template('signup.html', email=username)

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            flash("Signup Succesful", "success")
            session['username'] = username
            return redirect('/newpost')
        else:
            flash("User account already exists.", "error")
            return render_template('signup.html', email=username)

    return render_template('signup.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if not session['username']:
        redirect('/login')

    title_error = ''
    body_error = ''

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        owner = User.query.filter_by(username=session['username']).first()

        print("Owner ID: ", owner)

        if blog_title == '':
            title_error = 'Invalid Title'
        if blog_body == '':
            body_error = 'Invalid Entry'
        if title_error or body_error:
            return render_template('newpost.html', title='Add Blog Entry', title_error=title_error, body_error=body_error)

        else:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return render_template('blog.html', title=new_blog.title.title(), blog_body=new_blog.body)

    return render_template("newpost.html")

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    bloger_id = request.args.get('bloger')
    tilte = request.args.get('title')

    if bloger_id:
        bloger_blogs = Blog.query.filter_by(owner_id=bloger_id).all()
        bloger = User.query.filter_by(id=bloger_id).first().username
        return render_template('blog.html', bloger_blogs=bloger_blogs)

    blog_id = request.args.get('id')
    blogs = Blog.query.all()

    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('blog.html', title=blog.title.title(), blog_body=blog.body)

    return render_template("blog.html", all_blogs=blogs)

@app.route('/logout')
def logout():
    del session['username']
    flash("Logout Succesful", "success")
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
