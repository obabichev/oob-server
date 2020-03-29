import datetime

from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))

    posts = db.relationship('Post', backref='owner', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
        }


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.BigInteger, primary_key=True)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(20000))
    time_created = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
    title = db.Column(db.String(256), nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'owner': self.owner.serialize,
            'content': self.content,
        }
