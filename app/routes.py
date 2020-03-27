from app import app
from flask import request

from app.orm import get_posts, create_post, get_post


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
