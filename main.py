from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app) # This call SQLAlchemy constructtor and flask app is passed through it
app.secret_key = 'abcd123'

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key =True)
    title = db.Column(db.String(120))
    blog = db.Column(db.String(2000))
    
    def __init__(self, title, blog):
        self.title = title
        self.blog = blog

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        blog = request.form['blog']

        if len(title) == 0 or len(blog) == 0:
            flash("Title or Blog entry fields cannot be left empty")
            return render_template('newpost.html')


        new_post = Blog(title, blog)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog')
    else:
    #blogs = Blog.query.all()
        return render_template('newpost.html')

@app.route('/blog', methods=['POST', 'GET'])
def index():


#    if request.method == 'POST':  
#        blog = request.form['title', 'blog']   
 #       blogs.append(blog)
    blogs = Blog.query.all()
    return render_template('blog.html', blogs = blogs)

@app.route('/display-blog', methods=['POST'])
def display_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    return render_template('display.html', blog.title,blog.blog )
    

if __name__ == '__main__':

    app.run()