
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.contrib.github import make_github_blueprint
# from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
# from flask_caching import Cache
from flask_mail import Mail


app=Flask(__name__)
app.config['SECRET_KEY'] = 'Sid2983$&'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
ckeditor = CKEditor(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sid24000576@gmail.com'
app.config['MAIL_PASSWORD'] = 'ywediwpaaywfakgt'


mail = Mail(app)

# cache = Cache(app)

#google api blueprint
blueprint = make_google_blueprint(client_id='885804391863-epgi238upfo9unp0626o7460i661t2j4.apps.googleusercontent.com',client_secret='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',offline=True,scope=['profile','email'])
app.register_blueprint(blueprint,url_prefix='/login/google')

#github api blueprint
github_blueprint = make_github_blueprint(client_id='dea9604a2fb65920c7cf',client_secret='a6386089fb1c63b1e430d98333992fa983ba8b19',scope=['profile','login','user:email'])
app.register_blueprint(github_blueprint,url_prefix='/login/github')

from flaskblog import routes
