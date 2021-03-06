from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app) # This call SQLAlchemy constructtor and flask app is passed through it
app.secret_key = 'abcd123'

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password)

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, blog, owner):
        self.title = title
        self.blog = blog
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'home']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():  
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['email']= email
            flash("Logged in")
            return redirect('/home')
        else:
            flash("User password incorrect, or user does not exist", 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if ((email.count('@')==0) or (email.count('.')==0) or len(email)<3):
            flash('Please enter a valid Email address')
            return redirect('/signup')
        
        #if not is_email(email):
        #    flash('The "' + email +'" does not seem like an email address')
        #    return redirect('/signup')
        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('The "' + email +'" is already taken')
            return redirect('/signup')
        if len(password)<3:
            flash('Passsword is too short')
            return redirect('/signup')
        if password != verify:
            flash("password did not match")
            return redirect('/signup')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['email']= email
        return redirect('/home')
    else:
        return render_template('signup.html')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        blog = request.form['blog']

        if len(title) == 0 or len(blog) == 0:
            flash("Title or Blog entry fields cannot be left empty")
            return render_template('newpost.html')

        owner = User.query.filter_by(email=session['email']).first()
        blog = Blog(title, blog, owner)
        db.session.add(blog)
        db.session.commit()
        return render_template('display.html', blog = blog )
        #return redirect('/blog')
    else:
    #blogs = Blog.query.all()
        return render_template('newpost.html')

@app.route('/blog', methods=['POST', 'GET'])
def index():

    if request.args.get('user'):
        user_id = request.args.get('user')
        user = User.query.get(user_id)
        blogs = Blog.query.filter_by(owner=user).all()
        return render_template('singleUser.html', blogs=blogs)
    
    
    
    #if request.args.get('id'):
    #    blog_id = request.args.get('id')
     #   blog = Blog.query.filter_by(id=blog_id).first()
     #   return render_template('display.html', blog=blog)
    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.filter_by(id=blog_id).first()
        return render_template('display.html', blog=blog)# id=owner_id )

    blogs = Blog.query.all()
    return render_template('blog.html', blogs = blogs)

    owner_id = request.args.get('id')
    if owner_id:
        blogs = Blog.query.filter_by(id=owner_id).all()
        return render_template('blog.html', blogs = blogs)


    

    

@app.route('/logout', methods=['POST'])
def logout():
    del session["email"]
    return redirect('/blog')  

def user_list():
    #return User.query.get(user.email).all()
    #user_email = User.query.filter_by(email='user.email')
    #all_emails = user_email.all()
    #return [user.email for user in User.query.all()]
    user_list = User.query.all()
    return user_list

@app.route('/home', methods=['GET', 'POST'])
def display_user_list():
    

    return render_template('index.html', users = user_list())
    


    


#@app.route('/blog', methods=['GET','POST'])
#def display_blog():

 #   blog.id = int(request.args.get('blog.id', None))
 #   blog = Blog.query.get(blog_id)
    


   # blog_id = int(request.form['blog-id'])
   # blog = Blog.query.get(blog_id)

    #cur = mysql.connection.cursor()
    #cur.execute("SELECT title, blog FROM blog where blog.id = [blog.id]")
  #  return render_template('display.html', blog.title, blog.blog )
    

if __name__ == '__main__':

    app.run()