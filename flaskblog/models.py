

from flaskblog import db,login_manager,app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from sqlalchemy.orm.collections import attribute_mapped_collection

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.user_loader
def load_auth_user(oauth_user_id):
    return Ouser.query.get(int(oauth_user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(25), unique=True,nullable=False)
    email = db.Column(db.String(125), unique=True,nullable=False)
    img_file = db.Column(db.String(20),nullable=False,default='default1.jpeg')
    password = db.Column(db.String(60),nullable = False)
    posts = db.relationship('Post',backref='author',lazy=True)
    

    def get_reset_token(self,expires_sec=600):
        s = Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        
        except:
            return None

        return User.query.get(user_id)


    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.img_file}')"
        
class Ouser(db.Model, UserMixin):
    __tablename__ = 'oauthuser'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(25), unique=True,nullable=False)
    email = db.Column(db.String(125), unique=True,nullable=False)
    img_file = db.Column(db.String(20),nullable=False,default='default1.jpeg')
    # posts = db.relationship('Post',backref='oauthor',lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.img_file}')"


class Post(db.Model):
        id = db.Column(db.Integer,primary_key=True)
        title =db.Column(db.String(400), unique=True,nullable=False)
        date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
        content = db.Column(db.Text,nullable=False)
        user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
        # oauth_user_id = db.Column(db.Integer,db.ForeignKey('ouser.id'),nullable=False)

        def __repr__(self):
            return f"User('{self.title}','{self.date_posted}')"

class OAuth(OAuthConsumerMixin, db.Model):
    __table_args__ = (db.UniqueConstraint("provider","provider_user_id"),)
    provider_user_id = db.Column(db.String(256),nullable= False)
    provider_user_login = db.Column(db.String(256),nullable= False)
    user_id = db.Column(db.Integer, db.ForeignKey('oauthuser.id'),nullable= False)
    user = db.relationship(Ouser,backref=db.backref("oauth",collection_class=attribute_mapped_collection("provider"),cascade="all, delete-orphan"))


# # collection_class=attribute_mapped_collection("provider")


