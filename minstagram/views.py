# -*- encoding=UTF-8 -*-

from minstagram import app
from flask import  render_template
from models import Image, User, Comment


@app.route('/')
def index():
	image = Image.query.order_by('id desc').limit(10).all()
	return render_template('index.html', image=image)

@app.route('/image/<image_id>')
def image(image_id):
	image = Image.query.get(image_id)
	return render_template('pageDetail.html', image=image)

@app.route('/profile/<user_id>')
def profile(user_id):
	user = User.query.get(user_id)
	return render_template('profile.html', user=user)

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template("500.html"), 500