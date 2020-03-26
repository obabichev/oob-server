from flask import jsonify
from app import db
from app.models import Post


def get_posts():
    posts = db.session.query(Post).all()
    _posts = [p.serialize for p in posts]
    print('_posts', posts)
    return jsonify(posts=_posts)


def create_post(title, owner_id, content):
    post = Post(title=title, owner_id=owner_id, content=content)
    db.session.add(post)
    db.session.commit()
    return jsonify(Post=post.serialize)


def get_post(post_id):
    post = db.session.query(Post).filter_by(id=post_id).one()
    return jsonify(post=post.serialize)
