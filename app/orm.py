from flask import jsonify
from flask_login import current_user
from sqlalchemy import or_, and_

from app import db
from app.models import Post


def get_posts():
    current_user_id = current_user.id if current_user.is_authenticated else None
    posts = Post.query \
        .filter(or_(Post.status == 'published', Post.owner_id == current_user_id)) \
        .filter(and_(Post.status != 'deleted', Post.status != 'init')).all()
    _posts = [p.serialize for p in posts]
    print('_posts', posts)
    return jsonify(posts=_posts)


def get_init_post():
    post = Post.query.filter_by(owner_id=current_user.id, status='init').first()
    if post is None:
        post = Post(owner_id=current_user.id, description='', content='', title='', status='init')
        db.session.add(post)
        db.session.commit()
    return jsonify(post=post.serialize)


def create_post(title, description, content):
    post = Post(title=title, owner_id=current_user.id, content=content, description=description)
    db.session.add(post)
    db.session.commit()
    return jsonify(post=post.serialize)


def get_post(post_id):
    post = db.session.query(Post).filter_by(id=post_id).one()
    return jsonify(post=post.serialize)
