# -*- encoding=UTF-8 -*-

from minstagram import app, db
from flask_script import Manager
from minstagram.models import User, Image, Comment
from random import randint

manage = Manager(app)

def get_image_url():
	return 'http://images.nowcoder.com/head/'+str(randint(0, 100))+'m.png'

@manage.command
def init_datebase():
	db.drop_all()
	db.create_all()
	for i in range(0, 100):
		db.session.add(User('profile'+str(i+1), 'password'+str(i+1), 'email'+str(i+1), 18700+i+1))
		for j in range(0, 3):
			db.session.add(Image(get_image_url(), i+1))
			for k in range(0, 3):
				db.session.add(Comment('This is a comment'+str(k), i+1, 3*i+j+1))

	db.session.commit()

	image = Image.query.get(1)
	comment = Comment.query.get(1)

	print comment.user

if __name__ == '__main__':
		manage.run()