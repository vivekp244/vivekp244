from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import current_user

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load configurations from config.py
app.config.from_object('config.Config')

# Initialize extensions after app creation
db = SQLAlchemy(app)  # Initialize SQLAlchemy
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Association table for many-to-many relationship between User and Role
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

# Models
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)  # Required by Flask-Security
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))

# Datastore for Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Forms
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

# Routes
@app.route('/')
def index():
    return render_template('index.html', title='Home')  # Render a home page with login and register buttons

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('blog_list.html', title='Dashboard')  # Protected dashboard view

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_datastore.create_user(email=form.email.data, password=form.password.data, fs_uniquifier=form.email.data)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html', title='Register', form=form)

@app.route('/blog/new', methods=['GET', 'POST'])
@login_required
def new_blog():
    form = BlogForm()
    if form.validate_on_submit():
        blog = Blog(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(blog)
        db.session.commit()
        flash('Your blog post has been created!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_blog.html', title='New Blog Post', form=form)

@app.route('/blog/<int:blog_id>')
@login_required
def blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return render_template('blog_detail.html', title=blog.title, blog=blog)

# Initialize database tables and run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created before the app runs
    app.run(debug=True)




# from dotenv import load_dotenv
# from datetime import datetime
# from flask import Flask, render_template, redirect, url_for, flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, TextAreaField, SubmitField
# from wtforms.validators import DataRequired, Email, EqualTo
# from flask_login import current_user
#
# # Load environment variables from .env file
# load_dotenv()
#
# # Initialize Flask app
# app = Flask(__name__)
#
# # Load configurations from config.py
# app.config.from_object('config.Config')
#
# # Initialize extensions after app creation
# db = SQLAlchemy(app)  # Initialize SQLAlchemy
# migrate = Migrate(app, db)  # Initialize Flask-Migrate
#
# # Association table for many-to-many relationship between User and Role
# roles_users = db.Table(
#     'roles_users',
#     db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#     db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
# )
#
# # Models
# class Role(db.Model, RoleMixin):
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))
#
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     active = db.Column(db.Boolean(), default=True)
#     fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)  # Required by Flask-Security
#     roles = db.relationship(
#         'Role',
#         secondary=roles_users,
#         backref=db.backref('users', lazy='dynamic')
#     )
#
# class Blog(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     date_posted = db.Column(db.DateTime, default=datetime.utcnow)
#     author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))
#
# # Datastore for Flask-Security
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)
#
# # Forms
# class RegistrationForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Sign Up')
#
# class BlogForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     content = TextAreaField('Content', validators=[DataRequired()])
#     submit = SubmitField('Post')
#
# # Routes
# @app.route('/')
# @login_required
# def index():
#     return render_template('blog_list.html')
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user_datastore.create_user(email=form.email.data, password=form.password.data, fs_uniquifier=form.email.data)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!', 'success')
#         return redirect(url_for('index'))
#     return render_template('register.html', title='Register', form=form)
#
# @app.route('/blog/new', methods=['GET', 'POST'])
# @login_required
# def new_blog():
#     form = BlogForm()
#     if form.validate_on_submit():
#         blog = Blog(title=form.title.data, content=form.content.data, author=current_user)
#         db.session.add(blog)
#         db.session.commit()
#         flash('Your blog post has been created!', 'success')
#         return redirect(url_for('index'))
#     return render_template('create_blog.html', title='New Blog Post', form=form)
#
# @app.route('/blog/<int:blog_id>')
# @login_required
# def blog(blog_id):
#     blog = Blog.query.get_or_404(blog_id)
#     return render_template('blog_detail.html', title=blog.title, blog=blog)
#
# # Initialize database tables and run the app
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # Ensure tables are created before the app runs
#     app.run(debug=True)






# ============================================================================================
# ============================================================================================
# ============================================================================================
# ============================================================================================





# from dotenv import load_dotenv
# load_dotenv()  # Load environment variables from .env file
#
# from datetime import datetime
# from flask import Flask, render_template, redirect, url_for, flash, request
# from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, TextAreaField, SubmitField
# from wtforms.validators import DataRequired, Email, EqualTo
# from flask_login import current_user
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
#
#
#
# # Initialize Flask app
# app = Flask(__name__)
#
# # Load configurations from config.py
# app.config.from_object('config.Config')
#
# # Initialize extensions after app creation
# db = SQLAlchemy(app)  # Initialize SQLAlchemy
# migrate = Migrate(app, db)  # Initialize Flask-Migrate
#
# # Association table for many-to-many relationship between User and Role
# roles_users = db.Table(
#     'roles_users',
#     db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#     db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
# )
#
# # Models
# class Role(db.Model, RoleMixin):
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))
#
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     active = db.Column(db.Boolean(), default=True)
#     fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)  # Required by Flask-Security
#     roles = db.relationship(
#         'Role',
#         secondary=roles_users,
#         backref=db.backref('users', lazy='dynamic')
#     )
#
# class Blog(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     date_posted = db.Column(db.DateTime, default=datetime.utcnow)
#     author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))
#
# # Datastore for Flask-Security
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)
#
# # Forms
# class RegistrationForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Sign Up')
#
# class BlogForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     content = TextAreaField('Content', validators=[DataRequired()])
#     submit = SubmitField('Post')
#
# # Routes
# @app.before_first_request
# def create_tables():
#     db.create_all()
#
# @app.route('/')
# @login_required
# def index():
#     return render_template('blog_list.html')
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user_datastore.create_user(email=form.email.data, password=form.password.data, fs_uniquifier=form.email.data)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!', 'success')
#         return redirect(url_for('index'))
#     return render_template('register.html', title='Register', form=form)
#
# @app.route('/blog/new', methods=['GET', 'POST'])
# @login_required
# def new_blog():
#     form = BlogForm()
#     if form.validate_on_submit():
#         blog = Blog(title=form.title.data, content=form.content.data, author=current_user)
#         db.session.add(blog)
#         db.session.commit()
#         flash('Your blog post has been created!', 'success')
#         return redirect(url_for('index'))
#     return render_template('create_blog.html', title='New Blog Post', form=form)
#
# @app.route('/blog/<int:blog_id>')
# @login_required
# def blog(blog_id):
#     blog = Blog.query.get_or_404(blog_id)
#     return render_template('blog_detail.html', title=blog.title, blog=blog)
#
# # if __name__ == '__main__':
# #     app.run(debug=True)
# # Ensure tables are created at startup
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)


# ============================================================================================
# ============================================================================================
# ============================================================================================
# ============================================================================================

# from dotenv import load_dotenv
# load_dotenv()
# from flask import Flask, render_template, redirect, url_for, flash, request
# from flask_sqlalchemy import SQLAlchemy
# from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
# from flask_migrate import Migrate
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, TextAreaField, SubmitField
# from wtforms.validators import DataRequired, Email, EqualTo
# from flask_login import current_user
# from datetime import datetime
#
# app = Flask(__name__)
# app.config.from_object('config.Config')  # Load configuration from config.py
#
# db = SQLAlchemy(app)  # Initialize SQLAlchemy
# migrate = Migrate(app, db)  # Initialize Flask-Migrate
#
# # Association table for many-to-many relationship between User and Role
# roles_users = db.Table(
#     'roles_users',
#     db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#     db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
# )
#
# # Models
# class Role(db.Model, RoleMixin):
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))
#
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     active = db.Column(db.Boolean(), default=True)
#     fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)  # Required by Flask-Security
#     roles = db.relationship(
#         'Role',
#         secondary=roles_users,
#         backref=db.backref('users', lazy='dynamic')
#     )
#
# class Blog(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     date_posted = db.Column(db.DateTime, default=datetime.utcnow)
#     author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))
#
# # Datastore for Flask-Security
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)
#
# # Forms
# class RegistrationForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Sign Up')
#
# class BlogForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     content = TextAreaField('Content', validators=[DataRequired()])
#     submit = SubmitField('Post')
#
# # Routes
# @app.before_first_request
# def create_tables():
#     db.create_all()
#
# @app.route('/')
# @login_required
# def index():
#     return render_template('blog_list.html')
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user_datastore.create_user(email=form.email.data, password=form.password.data, fs_uniquifier=form.email.data)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!', 'success')
#         return redirect(url_for('index'))
#     return render_template('register.html', title='Register', form=form)
#
# @app.route('/blog/new', methods=['GET', 'POST'])
# @login_required
# def new_blog():
#     form = BlogForm()
#     if form.validate_on_submit():
#         blog = Blog(title=form.title.data, content=form.content.data, author=current_user)
#         db.session.add(blog)
#         db.session.commit()
#         flash('Your blog post has been created!', 'success')
#         return redirect(url_for('index'))
#     return render_template('create_blog.html', title='New Blog Post', form=form)
#
# @app.route('/blog/<int:blog_id>')
# @login_required
# def blog(blog_id):
#     blog = Blog.query.get_or_404(blog_id)
#     return render_template('blog_detail.html', title=blog.title, blog=blog)
#
# if __name__ == '__main__':
#     app.run(debug=True)



# ==================================================================
# ===================================================================


# from flask import Flask, render_template, redirect, url_for, flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
# from flask_migrate import Migrate
#
# migrate = Migrate(app, db)
#
# app = Flask(__name__)
# # app.config.from_object('config.Config')
# app.config.from_object('config.Config')
#
# db = SQLAlchemy(app)
#
# roles_users = db.Table('roles_users',
#     db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#     db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
# )
#
# class Role(db.Model, RoleMixin):
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))
#
# # class User(db.Model, UserMixin):
# #     id = db.Column(db.Integer, primary_key=True)
# #     email = db.Column(db.String(255), unique=True)
# #     password = db.Column(db.String(255))
# #     active = db.Column(db.Boolean())
# #     roles = db.relationship('Role', secondary=roles_users,
# #                             backref=db.backref('users', lazy='dynamic'))
#
# # THIS CODE IS REPLACED HERE
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     active = db.Column(db.Boolean(), default=True)
#     fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)  # Required by Flask-Security
#     roles = db.relationship('Role', secondary=roles_users,
#                             backref=db.backref('users', lazy='dynamic'))
#
#
#
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
#
# security = Security(app, user_datastore)
#
# #
# # @app.before_first_request
# # def create_tables():
# #     db.create_all()
#
# @app.before_first_request
# def create_tables():
#     db.drop_all()  # Use only if it's safe to reset your database
#     db.create_all()
#
#
# @app.route('/')
# @login_required
# def index():
#     return render_template('blog_list.html')
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         form = RegistrationForm()
#         if form.validate_on_submit():
#             user_datastore.create_user(email=form.email.data, password=form.password.data)
#             db.session.commit()
#             flash('Congratulations, you are now a registered user!', 'success')
#             return redirect(url_for('login'))
#     else:
#         form = RegistrationForm()
#     return render_template('register.html', title='Register', form=form)
#
# @app.route('/blog/new', methods=['GET', 'POST'])
# @login_required
# def new_blog():
#     if request.method == 'POST':
#         form = BlogForm()
#         if form.validate_on_submit():
#             blog = Blog(title=form.title.data, content=form.content.data, author=current_user)
#             db.session.add(blog)
#             db.session.commit()
#             flash('Your blog post has been created!', 'success')
#             return redirect(url_for('index'))
#     else:
#         form = BlogForm()
#     return render_template('create_blog.html', title='New Blog Post', form=form)
#
# @app.route('/blog/<int:blog_id>')
# @login_required
# def blog(blog_id):
#     blog = Blog.query.get_or_404(blog_id)
#     return render_template('blog_detail.html', title=blog.title, blog=blog)
#
# class Blog(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     date_posted = db.Column(db.DateTime, default=datetime.utcnow)
#     author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     author = db.relationship('User', backref=db.backref('blog_posts', lazy=True))
#
# class RegistrationForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Sign Up')
#
# class BlogForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     content = TextAreaField('Content', validators=[DataRequired()])
#     submit = SubmitField('Post')
