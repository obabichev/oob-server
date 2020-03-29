from flask_login import login_user, current_user, logout_user

from app import app, User, db
from flask import request, jsonify

from app.orm import get_posts, create_post, get_post


@app.route('/api/register', methods=['POST'])
def register():
    content = request.get_json()
    user = User(username=content['username'],
                email=content['email'],
                first_name=content['firstName'],
                last_name=content['lastName'])
    user.set_password(content['password'])
    db.session.add(user)
    db.session.commit()
    print('user', user)
    print('user', user.serialize)
    login_user(user, remember=True)
    return jsonify(user=user.serialize)


@app.route('/api/login', methods=['POST'])
def login():
    content = request.get_json()

    email = content['email']
    password = content['password']

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify(error={'message': 'Wrong credentials'})

    login_user(user, remember=True)
    return jsonify(user=user.serialize)


@app.route('/api/user')
def get_current_user():
    if current_user.is_authenticated:
        return jsonify(user=current_user.serialize)
    return jsonify(user=None)


@app.route('/api/logout')
def logout():
    logout_user()
    return jsonify(None)


@app.route('/api/post', methods=['GET', 'POST'])
def posts():
    if request.method == 'GET':
        return get_posts()
    elif request.method == 'POST':
        title = request.args.get('title', '')
        owner_id = request.args.get('owner_id', '')
        content = request.args.get('content', '')
        return create_post(title, owner_id, content)


@app.route('/api/post/<id>', methods=['GET'])
def post(id):
    print('id', id)
    if request.method == 'GET':
        return get_post(id)
