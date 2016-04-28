import os
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, SQLAlchemyAdapter, UserManager
from flask_user import roles_required

from models import create_models
from config import ConfigClass

def create_app(test_config=None):                   # For automated tests
    # Setup Flask and read config from ConfigClass defined above
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')

    # Load local_settings.py if file exists         # For automated tests
    try: app.config.from_object('local_settings')
    except: pass

    # Load optional test_config                     # For automated tests
    if test_config:
        app.config.update(test_config)

    # Initialize Flask extensions
    mail = Mail(app)                                # Initialize Flask-Mail
    db = SQLAlchemy(app)                            # Initialize Flask-SQLAlchemy
    User, Role, UserRoles, Posts = create_models(db)

    # Reset all the database tables
    db.create_all()

    # Setup Flask-User
    db_adapter = SQLAlchemyAdapter(db,  User)
    user_manager = UserManager(db_adapter, app)

    # Create 'user007' user with 'secret' and 'agent' roles
    if not User.query.filter(User.username=='admin').first():
        user1 = User(username='admin', email='adambwinn@gmail.com', active=True,
                password=user_manager.hash_password('password'))
        user1.roles.append(Role(name='admin'))
        db.session.add(user1)
        db.session.commit()

    if len(Posts.query.all()) == 0:
        post = Posts(user_id=3, title='hello world', content='this is a test post to test the query')
        db.session.add(post)
        db.session.commit()

    # The Home page is accessible to anyone
    @app.route('/')
    @login_required
    def home_page():
        # posts = get_posts(db)
        posts = Posts.query.all()
        return render_template('main.html', posts=posts)

    @app.route('/post', methods=['GET', 'POST'])
    def new_post():
        if request.method == 'GET':
            return render_template('post_form.html')
        elif request.method == 'POST':
            form = request.form
            post = Posts(user_id=session['user_id'], title=form['title'], content=form['content'])
            db.session.add(post)
            db.session.commit()

            flash('post successful')
            return redirect(url_for('home_page'))



    # The Special page requires a user with 'special' and 'sauce' roles or with 'special' and 'agent' roles.
    @app.route('/admin')
    @roles_required('admin')   # Use of @roles_required decorator
    def special_page():
        return 'this isn\'t done yet'

    return app


# Start development web server
if __name__=='__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
