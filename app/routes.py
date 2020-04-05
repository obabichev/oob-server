import os

import boto3
from flask_login import login_user, current_user, logout_user
from werkzeug.utils import secure_filename

from app import app, User, db, BUCKET
from flask import request, jsonify, send_file

from app.models import File, Post
from app.orm import get_posts, create_post, get_post, get_draft_post
from app.utils.s3 import list_files, download_file, upload_file


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
        status = request.args.get('status')
        if status == 'draft':
            return get_draft_post()
        return get_posts()
    elif request.method == 'POST':
        body = request.get_json()

        title = body['title']
        description = body['description']
        content = body['content']

        # title = request.args.get('title', '')
        # owner_id = request.args.get('owner_id', '')
        # content = request.args.get('content', '')
        return create_post(title, description, content)


@app.route('/api/post/<id>', methods=['GET'])
def post(id):
    print('id', id)
    if request.method == 'GET':
        return get_post(id)


@app.route('/api/files')
def files():
    files = list_files(BUCKET)
    return jsonify(files=files)


@app.route("/api/file/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':
        return download_file(filename, BUCKET)
        # output = download_file(filename, BUCKET)
        # return send_file(output, as_attachment=True)


@app.route("/api/post/<post_id>/upload", methods=['POST'])
def upload(post_id):
    # print(request.files)
    f = request.files['file']
    # print(type(f))
    # print(f)

    post = Post.query.get(int(post_id))
    if post is None:
        return jsonify(error={'message': 'Post was not found'}), 400

    if not post.owner_id == current_user.id:
        return jsonify(error={'message': 'That is not your post'}), 400

    name = secure_filename(f.filename)
    print('postId', post_id)

    key = '{}/{}/{}'.format(current_user.id, post_id, name)

    mimetype = f.mimetype
    if not mimetype.startswith('image/'):
        return jsonify(error={'message': 'File should be an image'}), 400
    #
    s3_client = boto3.client('s3')
    s3_client.upload_fileobj(f, BUCKET, key, ExtraArgs={'ACL': 'public-read'})

    url = 'https://{}.s3.eu-central-1.amazonaws.com/{}'.format(BUCKET, key)

    file = File(url=url, key=key, filename=name, mimetype=mimetype, user_id=current_user.id, post_id=post.id)
    db.session.add(file)
    db.session.commit()

    return jsonify(file=file.serialize)

