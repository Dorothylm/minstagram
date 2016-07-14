# -*- encoding=UTF-8 -*-

from minstagram import app, db
from flask_script import Manager
from minstagram.models import User, Image, Comment
from random import randint
import random, hashlib
from flask import request

manage = Manager(app)

def get_image_url():
	return 'http://images.nowcoder.com/head/'+str(randint(0, 100))+'m.png'

@manage.command
def init_datebase():
	#db.drop_all()
	db.create_all()
	for i in range(0, 100):
		db.session.add(User('profile'+str(i+1), 'password'+str(i+1), '', 'email'+str(i+1), 18700+i+1))
		for j in range(0, 10):
			db.session.add(Image(get_image_url(), i+1))
			for k in range(0, 3):
				db.session.add(Comment('This is a comment'+str(k), i+1, 10*i+j+1))

	db.session.commit()


	comment = Comment.query.get(1)

	print comment.user

@manage.command
def test():
	test = {"images": [
		{"username": "profile100", "head_url": "http://images.nowcoder.com/head/44m.png", "user_id": 100,
		 "image_id": 1000, "created_time": "2016-07-05 14:14:28", "image_url": "http://images.nowcoder.com/head/3m.png",
		 "comments_count": 3, "comments": [{"username": "profile100", "content": "This is a comment0", "user_id": 100},
										   {"username": "profile100", "content": "This is a comment1",
											"user_id": 100}]}]}

	#print test["images"][0]["comments"][0]["username"]
	#print request.files
	#print dir(request.files)
	image = Image.query.filter_by(id=1).first()
	image.url = ssdfd
	print image




if __name__ == '__main__':
		manage.run()