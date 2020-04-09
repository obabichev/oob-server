import os

import boto3
from flask_login import login_user, current_user, logout_user
from werkzeug.utils import secure_filename

from app import app, User, db
from flask import request, jsonify, send_file

from app.models import File, Post
from app.orm import get_posts, create_post, get_post, get_init_post
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


@app.route('/api/post', methods=['GET'])
def posts():
    status = request.args.get('status')
    if status == 'init':
        return get_init_post()
    return get_posts()


@app.route('/api/post/<id>', methods=['GET'])
def post(id):
    print('id', id)
    if request.method == 'GET':
        return get_post(id)


@app.route('/api/files')
def files():
    files = list_files(app.config['S3_BUCKET_NAME'])
    return jsonify(files=files)


@app.route("/api/file/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':
        return download_file(filename, app.config['S3_BUCKET_NAME'])
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
    print('app.config[S3_BUCKET_NAME]', app.config['S3_BUCKET_NAME'])
    s3_client.upload_fileobj(f, app.config['S3_BUCKET_NAME'], key, ExtraArgs={'ACL': 'public-read'})

    url = 'https://{}.s3.eu-central-1.amazonaws.com/{}'.format(app.config['S3_BUCKET_NAME'], key)

    file = File(url=url, key=key, filename=name, mimetype=mimetype, user_id=current_user.id, post_id=post.id)
    db.session.add(file)
    db.session.commit()

    return jsonify(file=file.serialize)


@app.route("/api/post/<post_id>/files")
def post_files(post_id):
    post = Post.query.get(int(post_id))
    if post is None or not post.owner_id == current_user.id:
        return jsonify(error={'message': 'Post id is not correct'}), 400

    files = File.query.filter_by(post_id=post.id).order_by(File.created_at.desc()).all()

    serialized_files = [file.serialize for file in files]

    return jsonify(files=serialized_files)


@app.route('/api/post/<post_id>', methods=['PUT'])
def update_post(post_id):
    post = Post.query.get(int(post_id))
    if post is None or not post.owner_id == current_user.id:
        return jsonify(error={'message': 'Post id is not correct'}), 400

    body = request.get_json()
    post.title = body['title']
    post.description = body['description']
    post.content = body['content']
    post.status = body['status']
    db.session.commit()

    return post.serialize
