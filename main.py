from flask import Flask
from flask_gravatar import Gravatar
from models import db, User
from extensions import ckeditor, bootstrap, login_manager
from routes.auth import auth_bp
from routes.posts import posts_bp
from routes.pages import pages_bp
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///posts.db')

db.init_app(app)
ckeditor.init_app(app)
bootstrap.init_app(app)
login_manager.init_app(app)

gravatar = Gravatar(app, size=100, rating='g', default='retro',
                     force_default=False, force_lower=False,
                     use_ssl=False, base_url=None)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(pages_bp)



if __name__ == "__main__":
    app.run()