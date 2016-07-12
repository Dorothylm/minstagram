# -*-encoding=UTF-8-*-

from minstagram import db, login_manager
from random import randint
from datetime import datetime

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	content = db.Column(db.String(512))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
	status = db.Column(db.Integer, default=0) # 0 正常 1 删除
	user = db.relationship('User', backref='comment', uselist=False)

	def __init__(self, content, user_id, image_id):
		self.content = content
		self.user_id = user_id
		self.image_id = image_id

	def __repr__(self):
		return '<Comment %d %s>' %(Comment.id, Comment.content)

class Image(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	url = db.Column(db.String(512))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	created_time = db.Column(db.DateTime)
	comments = db.relationship('Comment', backref='image', lazy='dynamic')

	def __init__(self, url, user_id):
		self.url = url
		self.user_id = user_id
		self.created_time = datetime.now()

	def __repr__(self):
		return '<Image %d %s>' %(self.id, self.url)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	username = db.Column(db.String(64), unique=True)
	password = db.Column(db.String(32))
	salt = db.Column(db.String(32))
	email = db.Column(db.String(64), unique=True)
	phone_number = db.Column(db.Integer, unique=True)
	head_url = db.Column(db.String(128))
	images = db.relationship('Image', backref='user', lazy='dynamic')

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False;

	def get_id(self):
		return self.id

	def __init__(self, username, password, salt=None, email=None, phone_number=None):
		self.username = username
		self.password = password
		self.salt = salt
		self.email = email
		self.phone_number = phone_number
		self.head_url = 'http://images.nowcoder.com/head/'+str(randint(0, 100))+'m.png'

	def __repr__(self):
		return '<User %d %s>' %(self.id, self.username)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)